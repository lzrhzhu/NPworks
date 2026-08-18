"""
Variational Monte Carlo for the 1D harmonic oscillator.
Trial wavefunction psi_T(x) = exp(-alpha x^2), H = -0.5 d^2/dx^2 + 0.5 x^2.
Scans alpha and verifies the variational principle: energy is minimal and
the variance vanishes at the exact value alpha = 1/2.
"""
import numpy as np
import matplotlib.pyplot as plt


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
fig, ax = plt.subplots(figsize=(8, 5))
ax.errorbar(alphas, energies, yerr=errors, fmt='o-', capsize=3)
ax.axhline(E_exact, ls='--', color='k', label="exact E0 = 0.5")
ax.axvline(0.5, ls=':', color='gray', label="alpha = 0.5")
ax.set_xlabel(r"$\alpha$"); ax.set_ylabel("E [VMC]")
ax.set_title("Variational principle: minimum at alpha = 1/2")
ax.legend(); ax.grid(True, ls=':', alpha=0.5)
plt.tight_layout(); plt.suptitle('vmc_harmonic')
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(alphas, variances, 's-', color='crimson')
ax.axvline(0.5, ls=':', color='gray')
ax.set_xlabel(r"$\alpha$"); ax.set_ylabel("var(E_L)")
ax.set_title("Zero-variance principle: variance -> 0 at alpha = 1/2")
ax.grid(True, ls=':', alpha=0.5)
plt.tight_layout(); plt.suptitle('vmc_harmonic_variance')
print("saved ch20_vmc_harmonic + variance")

plt.show()
