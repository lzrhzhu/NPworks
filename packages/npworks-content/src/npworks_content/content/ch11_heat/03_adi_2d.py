import numpy as np
import matplotlib.pyplot as plt
import os


def _img_dir(ch):
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(d, "markdown")):
            return os.path.join(d, "markdown", "images", ch)
        d = os.path.dirname(d)
    out = os.path.join(os.path.expanduser("~"), "npworks_figures", ch)
    os.makedirs(out, exist_ok=True)
    return out


IMG_DIR = _img_dir("ch11")


def thomas_solve(a_val, b_val, c_val, d):
    n = len(d)
    cp = np.zeros(n); dp = np.zeros(n); x = np.zeros(n)
    cp[0] = c_val / b_val; dp[0] = d[0] / b_val
    for i in range(1, n):
        cp[i] = c_val / (b_val - a_val * cp[i - 1])
        dp[i] = (d[i] - a_val * dp[i - 1]) / (b_val - a_val * cp[i - 1])
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


Lx, Ly = 1.0, 1.0
Jx, Jy = 40, 40
alpha = 0.01
t_end = 2.0
dt = 0.01
dx = Lx / Jx
r = alpha * dt / dx ** 2
x = np.linspace(0, Lx, Jx + 1)
y = np.linspace(0, Ly, Jy + 1)
X, Y = np.meshgrid(x, y, indexing='ij')

T = np.zeros((Jx + 1, Jy + 1))
T[0, :] = 100.0
snapshot_times = [0, 0.1, 0.5, 1.0, 2.0]
snapshots = {0: T.copy()}
time_elapsed = 0.0
Nt = int(t_end / dt)

for n in range(Nt):
    T_half = T.copy()
    for j in range(1, Jy):
        rhs = (r / 2) * T[1:-1, j - 1] + (1 - r) * T[1:-1, j] + (r / 2) * T[1:-1, j + 1]
        rhs[0] += (r / 2) * T[0, j]
        rhs[-1] += (r / 2) * T[Jx, j]
        T_half[1:-1, j] = thomas_solve(-r / 2, 1 + r, -r / 2, rhs)
    T_new = T_half.copy()
    for i in range(1, Jx):
        rhs = (r / 2) * T_half[i - 1, 1:-1] + (1 - r) * T_half[i, 1:-1] + (r / 2) * T_half[i + 1, 1:-1]
        rhs[0] += (r / 2) * T_half[i, 0]
        rhs[-1] += (r / 2) * T_half[i, Jy]
        T_new[i, 1:-1] = thomas_solve(-r / 2, 1 + r, -r / 2, rhs)
    T = T_new
    T[0, :] = 100.0; T[-1, :] = 0.0; T[:, 0] = 0.0; T[:, -1] = 0.0
    T[0, 0] = 100.0; T[0, -1] = 100.0
    time_elapsed += dt
    for st in snapshot_times:
        if abs(time_elapsed - st) < dt / 2 and st not in snapshots:
            snapshots[st] = T.copy()

# 每个时刻一张独立图
first = True
for t_label in sorted(snapshots.keys()):
    T_plot = snapshots[t_label].T
    fig, ax = plt.subplots(figsize=(6, 5.5))
    pcm = ax.contourf(X.T, Y.T, T_plot, levels=20, cmap='hot')
    ax.contour(X.T, Y.T, T_plot, levels=10, colors='k', linewidths=0.3, alpha=0.5)
    plt.colorbar(pcm, ax=ax, label='T')
    ax.set_xlabel('$x$'); ax.set_ylabel('$y$')
    ax.set_title(f'$t = {t_label:.1f}$ s')
    ax.set_aspect('equal')
    plt.tight_layout()
    fname = "ch11_adi_2d.png" if first else f"ch11_adi_2d_t{t_label:.1f}.png"
    plt.savefig(os.path.join(IMG_DIR, fname), dpi=130)
    plt.close(fig)
    first = False

print(f"03_adi_2d.py done (r={r:.4f}, dt={dt}, Nt={Nt})")
