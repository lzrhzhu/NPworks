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


# 线性驱动阻尼摆:  d2θ/dt2 = -Ω²θ - q dθ/dt + F_D cos(Ω_D t)
g = 9.81
l = 1.0
Omega2 = g / l          # 固有频率平方
Omega = np.sqrt(Omega2)
q = 0.5                 # 阻尼系数
F_D = 0.5               # 驱动力幅值
dt = 0.005

# ---------- (1) 时间序列：暂态 -> 稳态周期振动 ----------
Omega_D = Omega * 0.9   # 驱动频率（接近固有频率，接近共振）
t_end = 60.0
n = int(t_end / dt)
t = np.zeros(n + 1)
theta = np.zeros(n + 1)
omega = np.zeros(n + 1)
theta[0] = 0.2
omega[0] = 0.0

for i in range(n):
    t[i + 1] = t[i] + dt
    omega[i + 1] = omega[i] + (-Omega2 * theta[i] - q * omega[i]
                               + F_D * np.cos(Omega_D * t[i])) * dt
    theta[i + 1] = theta[i] + omega[i + 1] * dt

# ---------- (2) 共振曲线：稳态振幅 vs 驱动频率 ----------
drive_freqs = np.linspace(0.5, 6.0, 120)
amps = np.zeros_like(drive_freqs)
t_meas_end = 120.0
nm = int(t_meas_end / dt)
for k, Od in enumerate(drive_freqs):
    th = 0.2
    om = 0.0
    n_transient = int(60.0 / dt)
    for i in range(n_transient):
        om = om + (-Omega2 * th - q * om + F_D * np.cos(Od * i * dt)) * dt
        th = th + om * dt
    tail = int(40.0 / dt)
    ths = np.empty(tail)
    for i in range(tail):
        tt = (n_transient + i) * dt
        om = om + (-Omega2 * th - q * om + F_D * np.cos(Od * tt)) * dt
        th = th + om * dt
        ths[i] = th
    amps[k] = 0.5 * (ths.max() - ths.min())

# --- 图1：时间序列（暂态 -> 稳态） ---
fig1, ax1 = plt.subplots(figsize=(9, 5))
ax1.plot(t, theta, 'b-', linewidth=0.8)
ax1.axvline(20.0, color='gray', linestyle='--', alpha=0.5,
            label='transient | steady')
ax1.set_xlabel('t (s)')
ax1.set_ylabel(r'$\theta$ (rad)')
ax1.set_title(rf'Linear Driven Damped Pendulum ($\Omega_D/\Omega={Omega_D/Omega:.2f}$)')
ax1.legend(loc='upper right', frameon=False)
plt.tight_layout()
plt.suptitle('linear_driven_pendulum')

# --- 图2：共振曲线（稳态振幅 vs 驱动频率） ---
fig2, ax2 = plt.subplots(figsize=(9, 5))
ax2.plot(drive_freqs, amps, 'r.-', markersize=4, linewidth=0.8)
ax2.axvline(Omega, color='gray', linestyle='--', alpha=0.6,
            label=rf'$\Omega={Omega:.2f}$')
ax2.set_xlabel(r'$\Omega_D$ (rad/s)')
ax2.set_ylabel('steady-state amplitude (rad)')
ax2.set_title('Resonance Curve')
ax2.legend(loc='upper right', frameon=False)
plt.tight_layout()
plt.suptitle('driven_resonance')

print("10_linear_driven.py done")

plt.show()
