"""
Diffusion Monte Carlo for the 1D harmonic oscillator ground state.
Walkers diffuse + drift + branch in imaginary time; the reference energy
E_T converges to the exact ground-state energy 0.5 (atomic units,
H = -0.5 d^2/dx^2 + 0.5 x^2). Also checks the time-step extrapolation.
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


def dmc_harmonic(dtau, n_target=2000, n_steps=6000, seed=0):
    rng = np.random.default_rng(seed)
    # guiding psi_T = exp(-x^2/2); log derivative -> drift v = d/dx ln psi = -x
    x = rng.normal(0.0, 1.0, n_target)
    E_T = 0.6   # initial guess (above 0.5)
    E_traj = []
    for step in range(n_steps):
        # 1. drift-diffusion (Euler-Maruyama): v_D = -x
        x = x - x * dtau + np.sqrt(dtau) * rng.normal(size=x.size)
        # local energy: -0.5 psi''/psi + 0.5 x^2 = 0.5 (constant for exact psi)
        EL = 0.5 * np.ones_like(x)
        # 2. branching weights
        w = np.exp(-(EL - E_T) * dtau)
        # 3. birth/death: number of copies m = floor(w + uniform)
        m = np.floor(w + rng.random(size=x.size)).astype(int)
        m = np.clip(m, 0, 3)
        x_new = np.repeat(x, m)
        # 4. population control
        n_pop = len(x_new)
        if n_pop == 0:
            x = rng.normal(0.0, 1.0, n_target)
        else:
            E_T += np.log(n_target / n_pop) / dtau
            # resample to ~n_target to avoid blowup/shrinkage
            idx = rng.integers(0, n_pop, size=n_target)
            x = x_new[idx]
        E_traj.append(E_T)
    E_traj = np.array(E_traj)
    # discard first half as equilibration
    return E_traj[len(E_traj) // 2:].mean(), E_traj


# --- run for several time steps, extrapolate to dtau -> 0 ---
dtaus = [0.10, 0.05, 0.02, 0.01]
Es = []
print(f"{'dtau':>6} {'E_T':>8}")
for dt in dtaus:
    E, _ = dmc_harmonic(dt, seed=0)
    Es.append(E)
    print(f"{dt:6.3f} {E:8.4f}")

# linear extrapolation to dtau=0
E0_ext = np.polyfit(dtaus, Es, 1)[1]
print(f"\nExtrapolated E0(dtau->0) = {E0_ext:.4f}  (exact 0.5)")

# --- plot: convergence trace for smallest dtau + extrapolation ---
E_conv, traj = dmc_harmonic(0.02, n_steps=4000, seed=0)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].plot(traj, color='darkgreen', lw=0.8)
axes[0].axhline(0.5, ls='--', color='k', label="exact E0 = 0.5")
axes[0].set_xlabel("imaginary-time step"); axes[0].set_ylabel("E_T")
axes[0].set_title("DMC reference energy converges to ground state")
axes[0].legend(); axes[0].grid(True, ls=':', alpha=0.5)
axes[1].plot(dtaus, Es, 'o-', color='crimson')
axes[1].plot([0] + dtaus, [E0_ext] + Es, '--', color='gray',
             label=f"extrapolate -> {E0_ext:.4f}")
axes[1].axhline(0.5, ls=':', color='k')
axes[1].set_xlabel("time step dtau"); axes[1].set_ylabel("E_T")
axes[1].set_title("Time-step extrapolation")
axes[1].legend(); axes[1].grid(True, ls=':', alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch20_dmc_harmonic.png"), dpi=130)
print("saved ch20_dmc_harmonic.png")
