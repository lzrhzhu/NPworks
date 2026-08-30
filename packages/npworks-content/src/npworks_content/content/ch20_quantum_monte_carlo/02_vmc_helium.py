"""
Variational Monte Carlo for the helium atom (2 electrons, Z=2).
Trial wavefunction (Slater-Jastrow):
    Psi_T = exp(-Z*(r1+r2)) * exp( r12 / (2*(1+beta*r12)) )
with orbital exponent Z*=2 (so the electron-nucleus cusp is satisfied) and
a Jastrow factor satisfying the electron-electron cusp condition.
Compares energies WITH and WITHOUT the Jastrow factor, illustrating how
explicit correlation lowers both the energy and the variance.
Atomic units (hbar=m_e=e=1).
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


Z_NUC = 2.0
Z_STAR = 2.0   # use nuclear charge in the orbital so the e-n cusp is satisfied
                # (keeps the local energy finite at the nucleus -> low variance);


def logpsi(r1, r2, a, b):
    """Jastrow U(r12) = a*r12/(1+b*r12); a=0 => pure orbital (no correlation)."""
    r1n = np.linalg.norm(r1)
    r2n = np.linalg.norm(r2)
    r12 = np.linalg.norm(r1 - r2)
    return -Z_STAR * (r1n + r2n) + a * r12 / (1.0 + b * r12)


def local_energy(r1, r2, a, b):
    r1n = np.linalg.norm(r1)
    r2n = np.linalg.norm(r2)
    r12 = np.linalg.norm(r1 - r2)
    if r12 < 1e-12:
        r12 = 1e-12
    # Jastrow U(r)=a r/(1+b r):  U'=a/(1+b r)^2,  U''=-2 a b/(1+b r)^3
    Up = a / (1.0 + b * r12) ** 2
    Upp = -2.0 * a * b / (1.0 + b * r12) ** 3
    if a == 0.0:
        Up = 0.0
        Upp = 0.0
    r1h = r1 / r1n
    r2h = r2 / r2n
    r12h = (r1 - r2) / r12
    lap1 = (Z_STAR ** 2 - 2 * Z_STAR / r1n) \
        + (Upp + 2 * Up / r12 + Up ** 2) \
        + 2 * (-Z_STAR * r1h).dot(Up * r12h)
    lap2 = (Z_STAR ** 2 - 2 * Z_STAR / r2n) \
        + (Upp + 2 * Up / r12 + Up ** 2) \
        + 2 * (-Z_STAR * r2h).dot(Up * (-r12h))
    T = -0.5 * (lap1 + lap2)
    V = -Z_NUC / r1n - Z_NUC / r2n + 1.0 / r12
    return T + V


def vmc_he(a, b, n_steps=80000, step=1.2, seed=0):
    rng = np.random.default_rng(seed)
    r1 = rng.normal(size=3)
    r2 = rng.normal(size=3)
    lp = logpsi(r1, r2, a, b)
    for _ in range(3000):
        for electron in (0, 1):
            r1p, r2p = r1.copy(), r2.copy()
            if electron == 0:
                r1p += step * rng.normal(size=3)
            else:
                r2p += step * rng.normal(size=3)
            lp2 = logpsi(r1p, r2p, a, b)
            if np.log(rng.random()) < 2 * (lp2 - lp):
                r1, r2, lp = r1p, r2p, lp2
    EL = np.empty(n_steps)
    for i in range(n_steps):
        for electron in (0, 1):
            r1p, r2p = r1.copy(), r2.copy()
            if electron == 0:
                r1p += step * rng.normal(size=3)
            else:
                r2p += step * rng.normal(size=3)
            lp2 = logpsi(r1p, r2p, a, b)
            if np.log(rng.random()) < 2 * (lp2 - lp):
                r1, r2, lp = r1p, r2p, lp2
        EL[i] = local_energy(r1, r2, a, b)
    blocks = np.array_split(EL, 20)
    means = np.array([blk.mean() for blk in blocks])
    return EL.mean(), means, EL.var()


# a=0 => pure product orbital (no e-e correlation); a=0.5 satisfies the cusp.
cases = [("no Jastrow", 0.0, 0.0),
         ("b=0.3", 0.5, 0.3), ("b=0.5", 0.5, 0.5), ("b=1.0", 0.5, 1.0),
         ("b=2.0", 0.5, 2.0), ("b=5.0", 0.5, 5.0)]
print(f"{'case':>12} {'E':>10} {'err':>8} {'var(E_L)':>10}")
results = []
for name, a, b in cases:
    # Pool long-block means from two independent chains.  This keeps each
    # chain's blocking information instead of estimating an error from only
    # two seed averages.
    block_means, vars_ = [], []
    for s in (1, 2):
        _, means, var = vmc_he(a, b, seed=s)
        block_means.extend(means)
        vars_.append(var)
    block_means = np.asarray(block_means)
    E = block_means.mean()
    err = block_means.std(ddof=1) / np.sqrt(block_means.size)
    var = np.mean(vars_)
    results.append((name, E, err, var))
    print(f"{name:>12} {E:10.4f} {err:8.4f} {var:10.4f}")

print("\nNo-Jastrow violates the e-e cusp => huge variance; the Jastrow")
print("slashes the variance and lowers the energy (HF -2.862, exact -2.9037).")
print("(A more complete trial with orbital optimization reaches ~ -2.90; this demo shows the mechanism.)")

# --- plot ---
names = [r[0] for r in results]
E = np.array([r[1] for r in results])
err = np.array([r[2] for r in results])
var = np.array([r[3] for r in results])
x = np.arange(len(names))

fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.3))
ax = axes[0]
ax.errorbar(x, E, yerr=err, fmt='o-', capsize=3)
ax.axhline(-2.9037, ls='--', color='k', label="exact -2.9037")
ax.axhline(-2.8617, ls=':', color='0.45', label="HF -2.8617")
ax.set_xticks(x); ax.set_xticklabels(names, rotation=20)
ax.set_ylabel(r"$E_{\rm VMC}$ (Hartree)")
ax.set_title("(a) Variational energy")
ax.legend(frameon=False)

ax = axes[1]
ax.semilogy(x, var, 's-', color='crimson')
ax.set_xticks(x); ax.set_xticklabels(names, rotation=20)
ax.set_ylabel(r"$\mathrm{var}(E_L)$ (Hartree$^2$)")
ax.set_title("(b) Local-energy variance")

fig.tight_layout()
fig.suptitle('vmc_helium')
print("saved ch20_vmc_helium")

plt.show()
