"""
Variational Monte Carlo for the 1D harmonic oscillator.
Trial wavefunction psi_T(x) = exp(-alpha x^2), H = -0.5 d^2/dx^2 + 0.5 x^2.
Scans alpha and verifies the variational principle: energy is minimal and
the variance vanishes at the exact value alpha = 1/2.
"""
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300,
    'figure.figsize': (6.4, 4.0),
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'axes.grid': False,
    'axes.unicode_minus': False,
})


def local_energy(alpha, x):
    """E_L = -0.5 (psi''/psi) + 0.5 x^2, with psi = exp(-alpha x^2)."""
    kin = alpha - 2.0 * alpha ** 2 * x ** 2     # -0.5 * (psi''/psi) = alpha - 2 alpha^2 x^2
    return kin + 0.5 * x ** 2


def vmc(alpha, n_steps=40000, step=2.0, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.normal(0.0, 1.0 / np.sqrt(2.0 * alpha))
    logp = -2.0 * alpha * x * x
    acc = 0
    samples = np.empty(n_steps)
    # thermalize
    for _ in range(2000):
        xp = x + step * rng.normal()
        logp2 = -2.0 * alpha * xp * xp
        if np.log(rng.random()) < logp2 - logp:
            x, logp = xp, logp2
    for i in range(n_steps):
        xp = x + step * rng.normal()
        logp2 = -2.0 * alpha * xp * xp
        if np.log(rng.random()) < logp2 - logp:
            x, logp = xp, logp2
            acc += 1
        samples[i] = x
    EL = local_energy(alpha, samples)
    # blocking estimate of error (10 blocks)
    blocks = np.array_split(EL, 10)
    means = np.array([b.mean() for b in blocks])
    return EL.mean(), means.std(ddof=1) / np.sqrt(10), EL.var()


alphas = np.linspace(0.2, 0.9, 15)
energies, errors, variances = [], [], []
for a in alphas:
    E, err, var = vmc(a)
    energies.append(E); errors.append(err); variances.append(var)
    print(f"alpha={a:.3f}  E={E:.4f} +- {err:.4f}  var={var:.4f}")

E_exact = 0.5
print(f"\nExact ground-state energy E0 = {E_exact} (at alpha=0.5)")

# --- plot ---
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
ax = axes[0]
ax.errorbar(alphas, energies, yerr=errors, fmt='o-', capsize=3,
            label="VMC samples")
ax.axhline(E_exact, ls='--', color='k', label=r"exact $E_0=0.5$")
ax.axvline(0.5, ls=':', color='0.45', label=r"$\alpha=0.5$")
ax.set_xlabel(r"$\alpha$ (dimensionless)")
ax.set_ylabel(r"$E_{\rm VMC}$ (Hartree)")
ax.set_title("(a) Variational energy")
ax.legend(frameon=False)
ax.minorticks_on()

ax = axes[1]
ax.plot(alphas, variances, 's-', color='crimson')
ax.axvline(0.5, ls=':', color='0.45')
ax.set_xlabel(r"$\alpha$ (dimensionless)")
ax.set_ylabel(r"$\mathrm{var}(E_L)$ (Hartree$^2$)")
ax.set_title("(b) Local-energy variance")
ax.minorticks_on()

fig.tight_layout()
fig.suptitle('vmc_harmonic')
print("saved ch20_vmc_harmonic")

plt.show()
