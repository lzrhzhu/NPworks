"""Importance-sampled DMC for the 1D harmonic oscillator.

The deliberately inexact guide psi_T=exp(-alpha*x^2), alpha=0.4, has VMC
energy 0.5125 Hartree. DMC projects its mixed energy toward the exact 0.5.
Independent replicas quantify time-step and finite-population effects.
"""
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10,
    'xtick.direction': 'in', 'ytick.direction': 'in',
    'xtick.top': True, 'ytick.right': True, 'axes.linewidth': 0.8,
    'lines.linewidth': 1.5, 'lines.markersize': 5, 'axes.grid': False,
    'axes.unicode_minus': False,
})

ALPHA = 0.4
E_EXACT = 0.5
E_VMC = ALPHA / 2.0 + 1.0 / (8.0 * ALPHA)


def log_psi(x):
    return -ALPHA * x * x


def drift(x):
    """Importance-sampling drift d ln(psi_T) / dx."""
    return -2.0 * ALPHA * x


def local_energy(x):
    return ALPHA + (0.5 - 2.0 * ALPHA ** 2) * x * x


def systematic_resample(weights, rng):
    n_walkers = weights.size
    positions = (rng.random() + np.arange(n_walkers)) / n_walkers
    cumulative = np.cumsum(weights)
    cumulative[-1] = 1.0
    return np.searchsorted(cumulative, positions)


def dmc_harmonic(dtau, n_walkers=1000, n_steps=2400, burn_in=600, seed=0):
    rng = np.random.default_rng(seed)
    # |psi_T|^2 ~ exp(-2*alpha*x^2), so its variance is 1/(4*alpha).
    x = rng.normal(0.0, 1.0 / (2.0 * np.sqrt(ALPHA)), n_walkers)
    e_ref = E_VMC
    mixed_trace = np.empty(n_steps)
    accept_trace = np.empty(n_steps)

    for step in range(n_steps):
        x_old = x.copy()
        e_old = local_energy(x_old)
        x_proposed = (x_old + drift(x_old) * dtau
                      + np.sqrt(dtau) * rng.normal(size=n_walkers))
        forward = x_proposed - x_old - drift(x_old) * dtau
        backward = x_old - x_proposed - drift(x_proposed) * dtau
        log_accept = (2.0 * (log_psi(x_proposed) - log_psi(x_old))
                      - (backward ** 2 - forward ** 2) / (2.0 * dtau))
        accepted = np.log(rng.random(n_walkers)) < np.minimum(0.0, log_accept)
        x = np.where(accepted, x_proposed, x_old)
        e_new = local_energy(x)

        # Symmetric branching. Raising e_ref raises all weights, so the
        # feedback lowers e_ref when the implied population grows.
        log_weights = dtau * (e_ref - 0.5 * (e_old + e_new))
        log_mean_weight = np.logaddexp.reduce(log_weights) - np.log(n_walkers)
        e_ref -= 0.5 * log_mean_weight / dtau
        weights = np.exp(log_weights - np.max(log_weights))
        weights /= weights.sum()
        x = x[systematic_resample(weights, rng)]

        mixed_trace[step] = local_energy(x).mean()
        accept_trace[step] = accepted.mean()

    production = mixed_trace[burn_in:]
    blocks = np.array_split(production, 12)
    block_means = np.array([block.mean() for block in blocks])
    error = block_means.std(ddof=1) / np.sqrt(block_means.size)
    return production.mean(), error, mixed_trace, accept_trace[burn_in:].mean()


def replicated_result(dtau, n_walkers, seeds=(1, 2, 3, 4)):
    estimates, errors = [], []
    for seed in seeds:
        energy, error, _, _ = dmc_harmonic(
            dtau, n_walkers=n_walkers, seed=seed
        )
        estimates.append(energy)
        errors.append(error)
    estimates = np.asarray(estimates)
    within = np.sqrt(np.sum(np.asarray(errors) ** 2)) / len(seeds)
    between = estimates.std(ddof=1) / np.sqrt(len(seeds))
    return estimates.mean(), max(within, between)


dtau_values = np.array([0.20, 0.10, 0.05, 0.02])
time_energies, time_errors = [], []
print(f"guide alpha={ALPHA:.2f}: VMC={E_VMC:.6f}, exact={E_EXACT:.6f}")
print(f"{'dtau':>7} {'E_mix':>10} {'error':>10}")
for dtau in dtau_values:
    energy, error = replicated_result(dtau, n_walkers=1000)
    time_energies.append(energy)
    time_errors.append(error)
    print(f"{dtau:7.3f} {energy:10.6f} {error:10.6f}")

fit = np.polyfit(dtau_values, time_energies, 1,
                 w=1.0 / np.maximum(time_errors, 1.0e-8))
e_extrapolated = fit[1]
print(f"zero-time-step extrapolation: {e_extrapolated:.6f}")

population_values = np.array([250, 1000, 4000])
population_energies, population_errors = [], []
print(f"\n{'walkers':>8} {'E_mix':>10} {'error':>10}")
for n_walkers in population_values:
    energy, error = replicated_result(0.05, n_walkers=n_walkers)
    population_energies.append(energy)
    population_errors.append(error)
    print(f"{n_walkers:8d} {energy:10.6f} {error:10.6f}")

trace_energy, _, trace, acceptance = dmc_harmonic(
    0.05, n_walkers=1000, n_steps=1800, burn_in=400, seed=11
)
print(f"\ntrace run: E_mix={trace_energy:.6f}, acceptance={acceptance:.3f}")

fig, axes = plt.subplots(1, 3, figsize=(10.0, 3.2))
ax = axes[0]
tau = 0.05 * np.arange(trace.size)
running_mean = np.cumsum(trace) / np.arange(1, trace.size + 1)
ax.plot(tau, trace, color='tab:blue', lw=0.8, alpha=0.22,
        label=r"instantaneous $E$")
ax.plot(tau, running_mean, color='tab:blue', lw=1.8,
        label="cumulative mean")
ax.axhline(E_VMC, ls=':', color='0.45', label="VMC")
ax.axhline(E_EXACT, ls='--', color='k', label="exact")
ax.set_xlabel(r"$\tau$ (Hartree$^{-1}$)")
ax.set_ylabel(r"$E_{\rm mix}$ (Hartree)")
ax.set_title("(a) Projection")
ax.legend(frameon=False)

ax = axes[1]
ax.errorbar(dtau_values, time_energies, yerr=time_errors,
            fmt='o', capsize=3, label="DMC")
line_dtau = np.linspace(0.0, dtau_values.max(), 100)
ax.plot(line_dtau, np.polyval(fit, line_dtau), '--', color='tab:red',
        label="linear fit")
ax.axhline(E_EXACT, ls=':', color='k', label="exact")
ax.set_xlabel(r"$\Delta\tau$ (Hartree$^{-1}$)")
ax.set_ylabel(r"$E_{\rm mix}$ (Hartree)")
ax.set_title("(b) Time-step test")
ax.legend(frameon=False)

ax = axes[2]
inverse_population = 1.0 / population_values
order = np.argsort(inverse_population)
ax.errorbar(inverse_population[order], np.asarray(population_energies)[order],
            yerr=np.asarray(population_errors)[order], fmt='s-', capsize=3,
            color='tab:green')
ax.axhline(E_EXACT, ls='--', color='k', label="exact")
ax.set_xlabel(r"$1/M$ (walker$^{-1}$)")
ax.set_ylabel(r"$E_{\rm mix}$ (Hartree)")
ax.set_title("(c) Population test")
ax.legend(frameon=False)

fig.tight_layout()
fig.suptitle('dmc_harmonic')
plt.show()
