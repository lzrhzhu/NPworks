import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'lines.markersize': 5,
    'axes.grid': False, 'axes.unicode_minus': False,
})


# Fermi-Pasta-Ulam-Tsingou alpha 模型（固定端，原始 1955 形式）
#   x_i'' = (x_{i+1}-2x_i+x_{i-1}) + alpha[(x_{i+1}-x_i)^2 - (x_i-x_{i-1})^2]
# 二次（alpha）非线性使能量在各简正模之间转移，并出现著名的"递归"现象。
N = 32                 # 内部粒子数
alpha = 1.0
A = 1.0

i = np.arange(1, N + 1)
x = A * np.sin(np.pi * i / (N + 1))     # 初始为第 1 简正模
v = np.zeros(N)

# 简正模矩阵与频率（线性链）
S = np.sin(np.pi * np.outer(i, i) / (N + 1)) * np.sqrt(2.0 / (N + 1))  # Q = S @ x
omega2 = 2.0 * (1.0 - np.cos(np.pi * i / (N + 1)))


def accel(xx):
    xpad = np.concatenate(([0.0], xx, [0.0]))
    dx = xpad[1:] - xpad[:-1]                       # 弹簧伸长量（含端点）
    lin = dx[1:] - dx[:-1]                          # x_{i+1}-2x_i+x_{i-1}
    nl = alpha * (dx[1:] ** 2 - dx[:-1] ** 2)
    return lin + nl


def mode_energies(xx, vv):
    Q = S @ xx
    V = S @ vv
    return 0.5 * (V ** 2 + omega2 * Q ** 2)


dt = 0.02
t_end = 600.0
n_steps = int(t_end / dt)
rec_every = 5
n_rec = n_steps // rec_every + 1

times = np.zeros(n_rec)
Emode = np.zeros((n_rec, N))
idx = 0
Emode[0] = mode_energies(x, v)

a = accel(x)
for step in range(1, n_steps + 1):
    # velocity Verlet
    v = v + 0.5 * dt * a
    x = x + dt * v
    a = accel(x)
    v = v + 0.5 * dt * a
    if step % rec_every == 0:
        idx += 1
        times[idx] = step * dt
        Emode[idx] = mode_energies(x, v)

Etot0 = Emode[0].sum()

fig, ax = plt.subplots(figsize=(10, 5.5))
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
for n in range(1, 5):
    ax.plot(times, Emode[:, n - 1] / Etot0, color=colors[n - 1], linewidth=1.0,
            label=rf'mode {n}')
ax.set_xlabel('t')
ax.set_ylabel(r'$E_n / E_{\mathrm{tot}}$')
ax.set_title('FPUT Recurrence: energy returns to mode 1 instead of equipartition')
ax.set_xlim(0, t_end)
ax.set_ylim(0, 1.02)
ax.legend(loc='center right', frameon=False)
plt.tight_layout()
plt.suptitle('fput_recurrence')

print("08_fput_recurrence.py done")

plt.show()
