"""
Strange-attractor fractal dimension: integrate the Lorenz system, then
estimate the correlation dimension D2 via the Grassberger-Procaccia
algorithm (C(r) ~ r^D2). Expected D2 ~ 2.05.
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


IMG_DIR = _img_dir("ch22")


def lorenz_integrate(sigma=10.0, rho=28.0, beta=8.0 / 3.0,
                     dt=0.01, n_steps=20000, x0=(1.0, 1.0, 1.0)):
    x = np.array(x0, dtype=float)
    traj = np.empty((n_steps, 3))
    for i in range(n_steps):
        dx = sigma * (x[1] - x[0])
        dy = x[0] * (rho - x[2]) - x[1]
        dz = x[0] * x[1] - beta * x[2]
        x = x + dt * np.array([dx, dy, dz])  # RK1; fine for attractor sampling
        traj[i] = x
    return traj


def correlation_integral(traj, rs):
    """C(r) = fraction of pairs with distance < r."""
    n = len(traj)
    # subsample for speed if large
    if n > 4000:
        idx = np.linspace(0, n - 1, 4000).astype(int)
        traj = traj[idx]
        n = len(traj)
    # pairwise distance via broadcasting
    diff = traj[:, None, :] - traj[None, :, :]
    d = np.sqrt((diff ** 2).sum(axis=2))
    d = d[np.triu_indices(n, k=1)]
    C = np.array([(d < r).mean() for r in rs])
    return C


# --- Lorenz attractor ---
traj = lorenz_integrate(n_steps=15000)[2000:]   # drop transient
rs = np.logspace(-0.5, 1.8, 30)
C = correlation_integral(traj, rs)

# --- fit D2 in the scaling region ---
fit = (C > 1e-3) & (C < 0.3) & np.isfinite(C)
D2 = np.polyfit(np.log(rs[fit]), np.log(C[fit]), 1)[0]
print(f"Lorenz correlation dimension D2 ~ {D2:.3f}  (expected ~2.05)")

# --- plot ---
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
axes[0].plot(traj[:, 0], traj[:, 2], lw=0.3, color='darkblue')
axes[0].set_xlabel("x"); axes[0].set_ylabel("z")
axes[0].set_title("Lorenz strange attractor")
axes[1].loglog(rs, C, 'o-', color='crimson')
axes[1].loglog(rs[fit], (rs[fit] ** D2) * np.exp(np.log(C[fit][0]) - D2 * np.log(rs[fit][0])),
               'k--', label=f"slope D2 = {D2:.3f}")
axes[1].set_xlabel("r"); axes[1].set_ylabel("C(r)")
axes[1].set_title("Grassberger-Procaccia")
axes[1].legend(); axes[1].grid(True, which='both', ls=':', alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch22_lorenz_correlation.png"), dpi=130)
print("saved ch22_lorenz_correlation.png")
