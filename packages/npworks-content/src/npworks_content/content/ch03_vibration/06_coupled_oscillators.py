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


# 两个相同单摆的小角耦合方程 (3.6)：theta1'' = -Omega2*theta1 + kappa*(theta2-theta1)
#                                              theta2'' = -Omega2*theta2 - kappa*(theta2-theta1)
# 与正文 3.2.3 节一致：Euler-Cromer 多自由度推广（辛，能量误差有界振荡）
Omega2 = 9.81        # Omega^2 = g/l, l = 1.0
kappa = 2.0          # 耦合强度 kappa = k*d^2/(m*l^2)
theta1_0 = 0.3       # 初始只激发第一个摆
theta2_0 = 0.0

dt = 0.002
t_end = 120.0
t = np.arange(0.0, t_end, dt)
N = len(t)

theta = np.zeros((N, 2))
omega = np.zeros((N, 2))
theta[0] = [theta1_0, theta2_0]
omega[0] = [0.0, 0.0]
for i in range(N - 1):
    t1, t2 = theta[i]
    # 第一步：用旧角度更新全部角速度（式 (3.6) 右端）
    w1 = omega[i, 0] + dt * (-Omega2 * t1 + kappa * (t2 - t1))
    w2 = omega[i, 1] + dt * (-Omega2 * t2 - kappa * (t2 - t1))
    # 第二步：用新角速度更新全部角度
    theta[i + 1] = [t1 + dt * w1, t2 + dt * w2]
    omega[i + 1] = [w1, w2]

# 各摆的局部能量（以 m*l^2 为单位，仅取各摆动能与主恢复力势能，耦合弹簧能不归属单摆）
E1 = 0.5 * omega[:, 0] ** 2 + 0.5 * Omega2 * theta[:, 0] ** 2
E2 = 0.5 * omega[:, 1] ** 2 + 0.5 * Omega2 * theta[:, 1] ** 2
Etot = E1 + E2
E1f = E1 / Etot
E2f = E2 / Etot

# 简正模频率与拍频（核对数值结果）
om_1 = np.sqrt(Omega2)                    # 同相模
om_2 = np.sqrt(Omega2 + 2.0 * kappa)      # 反相模
om_beat = om_2 - om_1
print(f"om_1 = {om_1:.4f}, om_2 = {om_2:.4f}")
print(f"om_beat = {om_beat:.4f}, "
      f"t_transfer = {np.pi / om_beat:.3f} s, T_exchange = {2 * np.pi / om_beat:.3f} s")

fig, ax1 = plt.subplots(figsize=(10, 4.5))
ax1.plot(t, theta[:, 0], 'b-', linewidth=0.6, label=r'$\theta_1$')
ax1.plot(t, theta[:, 1], 'r--', linewidth=0.8, label=r'$\theta_2$')
ax1.set_xlabel('t (s)')
ax1.set_ylabel(r'$\theta$ (rad)')
ax1.set_title('Coupled Pendula: Beat Phenomenon (energy shuttles between the two)')
ax1.legend(loc='upper right', ncol=2, frameon=False)
plt.tight_layout(); plt.suptitle('coupled_oscillators')

fig, ax2 = plt.subplots(figsize=(10, 4.5))
ax2.plot(t, E1f, 'b-', linewidth=1.0, label=r'$E_1/E_{tot}$')
ax2.plot(t, E2f, 'r--', linewidth=1.0, label=r'$E_2/E_{tot}$')
ax2.set_xlabel('t (s)')
ax2.set_ylabel('energy fraction')
ax2.set_title('Energy Transfer between the Two Oscillators')
ax2.legend(loc='upper right', frameon=False)
ax2.set_ylim(-0.05, 1.05)
plt.tight_layout(); plt.suptitle('coupled_oscillators_energy')
print("06_coupled_oscillators.py done")

plt.show()
