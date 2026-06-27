"""
Variational Monte Carlo for the 1D harmonic oscillator.
Trial wavefunction psi_T(x) = exp(-alpha x^2), H = -0.5 d^2/dx^2 + 0.5 x^2.
Scans alpha and verifies the variational principle: energy is minimal and
the variance vanishes at the exact value alpha = 1/2.
"""
import numpy as np
import matplotlib.pyplot as plt
import os


def _img_dir(ch):
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(d, "markdown")):
            return os.path.join(d, "markdown", "images", ch)
        d = os.path.dirname(d)
    # 未找到教材 markdown/images（PyPI 安装或独立运行）：回退到用户可写目录
    out = os.path.join(os.path.expanduser("~"), "npworks_figures", ch)
    os.makedirs(out, exist_ok=True)
    return out


IMG_DIR = _img_dir("ch20")


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
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].errorbar(alphas, energies, yerr=errors, fmt='o-', capsize=3)
axes[0].axhline(E_exact, ls='--', color='k', label="exact E0 = 0.5")
axes[0].axvline(0.5, ls=':', color='gray', label="alpha = 0.5")
axes[0].set_xlabel(r"$\alpha$"); axes[0].set_ylabel("E [VMC]")
axes[0].set_title("Variational principle: minimum at alpha = 1/2")
axes[0].legend(); axes[0].grid(True, ls=':', alpha=0.5)
axes[1].plot(alphas, variances, 's-', color='crimson')
axes[1].axvline(0.5, ls=':', color='gray')
axes[0].axhline  # noop
axes[1].set_xlabel(r"$\alpha$"); axes[1].set_ylabel("var(E_L)")
axes[1].set_title("Zero-variance principle: variance -> 0 at alpha = 1/2")
axes[1].grid(True, ls=':', alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch20_vmc_harmonic.png"), dpi=130)
print("saved ch20_vmc_harmonic.png")
