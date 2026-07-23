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


def thomas_solve(a, b, c, d):
    n = len(d)
    cp = np.zeros(n); dp = np.zeros(n); x = np.zeros(n)
    cp[0] = c[0] / b[0]; dp[0] = d[0] / b[0]
    for i in range(1, n):
        cp[i] = c[i] / (b[i] - a[i] * cp[i - 1])
        dp[i] = (d[i] - a[i] * dp[i - 1]) / (b[i] - a[i] * cp[i - 1])
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


def cn_step(T, r, T_left, T_right):
    J = len(T) - 1
    n_inner = J - 1
    a_vec = np.full(n_inner, -r / 2)
    b_vec = np.full(n_inner, 1 + r)
    c_vec = np.full(n_inner, -r / 2)
    rhs = np.zeros(n_inner)
    for idx in range(n_inner):
        j = idx + 1
        rhs[idx] = (r / 2) * T[j - 1] + (1 - r) * T[j] + (r / 2) * T[j + 1]
    rhs[0] += (r / 2) * T_left
    rhs[-1] += (r / 2) * T_right
    T_inner = thomas_solve(a_vec, b_vec, c_vec, rhs)
    T_new = T.copy()
    T_new[1:-1] = T_inner
    T_new[0] = T_left
    T_new[-1] = T_right
    return T_new


L = 1.0
Nx = 50
alpha = 0.01
t_end = 10.0
dx = L / Nx
T_left, T_right = 100.0, 0.0
x = np.linspace(0, L, Nx + 1)
T_ss = T_left + (T_right - T_left) * x / L
snapshot_times = [0, 0.5, 1.0, 2.0, 5.0, 10.0]
colors = plt.cm.viridis(np.linspace(0, 1, len(snapshot_times)))

# FTCS
r_ftcs = 0.4
dt_ftcs = r_ftcs * dx ** 2 / alpha
Nt_ftcs = int(t_end / dt_ftcs)
T_ftcs = np.zeros(Nx + 1); T_ftcs[0] = T_left; T_ftcs[-1] = T_right
time_elapsed = 0.0
snapshots_ftcs = {0: T_ftcs.copy()}
for n in range(Nt_ftcs):
    T_ftcs[1:-1] = T_ftcs[1:-1] + r_ftcs * (np.roll(T_ftcs, -1)[1:-1] - 2 * T_ftcs[1:-1] + np.roll(T_ftcs, 1)[1:-1])
    T_ftcs[0] = T_left; T_ftcs[-1] = T_right
    time_elapsed += dt_ftcs
    for st in snapshot_times:
        if abs(time_elapsed - st) < dt_ftcs / 2 and st not in snapshots_ftcs:
            snapshots_ftcs[st] = T_ftcs.copy()

# CN
r_cn = 5.0
dt_cn = r_cn * dx ** 2 / alpha
Nt_cn = int(t_end / dt_cn)
T_cn = np.zeros(Nx + 1); T_cn[0] = T_left; T_cn[-1] = T_right
time_elapsed = 0.0
snapshots_cn = {0: T_cn.copy()}
for n in range(Nt_cn):
    T_cn = cn_step(T_cn, r_cn, T_left, T_right)
    time_elapsed += dt_cn
    for st in snapshot_times:
        if abs(time_elapsed - st) < dt_cn / 2 and st not in snapshots_cn:
            snapshots_cn[st] = T_cn.copy()

# --- 图1：FTCS 快照 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
for idx, t_label in enumerate(sorted(snapshots_ftcs.keys())):
    ax.plot(x, snapshots_ftcs[t_label], color=colors[idx], label=f'$t = {t_label:.1f}$ s')
ax.plot(x, T_ss, 'k--', linewidth=2, label='Steady state')
ax.set_xlabel('Position $x$ (m)'); ax.set_ylabel('Temperature $T$')
ax.set_title(f'FTCS ($r = {r_ftcs}$, $\\Delta t = {dt_ftcs:.4f}$)')
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch11_cn_ftcs.png"), dpi=130)
plt.close(fig)

# --- 图2：CN 快照 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
for idx, t_label in enumerate(sorted(snapshots_cn.keys())):
    ax.plot(x, snapshots_cn[t_label], color=colors[idx], label=f'$t = {t_label:.1f}$ s')
ax.plot(x, T_ss, 'k--', linewidth=2, label='Steady state')
ax.set_xlabel('Position $x$ (m)'); ax.set_ylabel('Temperature $T$')
ax.set_title(f'Crank-Nicolson ($r = {r_cn}$, $\\Delta t = {dt_cn:.4f}$)')
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch11_cn_method.png"), dpi=130)
plt.close(fig)

print(f"02_cn_method.py done (FTCS Nt={Nt_ftcs}, CN Nt={Nt_cn})")
