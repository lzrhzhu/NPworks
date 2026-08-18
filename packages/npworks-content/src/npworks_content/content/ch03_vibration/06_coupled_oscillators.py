import numpy as np
import matplotlib.pyplot as plt


# 两个相同质量的耦合摆（小角近似）
# m x1'' = -k x1 - kc (x1 - x2)
# m x2'' = -k x2 - kc (x2 - x1)
# 简正模：对称  om_s = sqrt(k/m)；反对称  om_a = sqrt((k + 2 kc)/m)
m = 1.0
k = 1.0
kc = 0.1          # 弱耦合 -> 明显的拍
om_s = np.sqrt(k / m)
om_a = np.sqrt((k + 2.0 * kc) / m)

dt = 0.002
t_end = 120.0
t = np.arange(0, t_end, dt)
N = len(t)

# 解析解：初始 x1=A, x2=0, 速度为 0
A = 1.0
x1 = A * np.cos((om_a + om_s) / 2.0 * t) * np.cos((om_a - om_s) / 2.0 * t)
x2 = A * np.sin((om_a + om_s) / 2.0 * t) * np.sin((om_a - om_s) / 2.0 * t)

# 各振子的能量（含耦合贡献时近似，这里用"动能+主弹簧势能+耦合势能分摊"）
# 简单起见：绘制 x1, x2 的位移拍，以及把每个质量"局部"能量作定性能量转移图
def local_energy(x1a, x2a):
    # 速度（中心差分）
    v1 = np.gradient(x1a, dt)
    v2 = np.gradient(x2a, dt)
    E1 = 0.5 * m * v1 ** 2 + 0.5 * k * x1a ** 2
    E2 = 0.5 * m * v2 ** 2 + 0.5 * k * x2a ** 2
    return E1, E2

E1, E2 = local_energy(x1, x2)
Etot = E1 + E2
E1f = E1 / Etot
E2f = E2 / Etot

fig, ax1 = plt.subplots(figsize=(10, 4.5))
ax1.plot(t, x1, 'b-', linewidth=0.6, label=r'$x_1$')
ax1.plot(t, x2, 'r-', linewidth=0.6, label=r'$x_2$')
ax1.set_xlabel('t (s)')
ax1.set_ylabel('displacement')
ax1.set_title('Coupled Pendula: Beat Phenomenon (energy shuttles between the two)')
ax1.legend(loc='upper right', ncol=2)
ax1.grid(True, alpha=0.3)
plt.tight_layout(); plt.suptitle('coupled_oscillators')
fig, ax2 = plt.subplots(figsize=(10, 4.5))
ax2.plot(t, E1f, 'b-', linewidth=1.0, label=r'$E_1/E_{tot}$')
ax2.plot(t, E2f, 'r-', linewidth=1.0, label=r'$E_2/E_{tot}$')
ax2.set_xlabel('t (s)')
ax2.set_ylabel('energy fraction')
ax2.set_title('Energy Transfer between the Two Oscillators')
ax2.legend(loc='upper right')
ax2.set_ylim(-0.05, 1.05)
ax2.grid(True, alpha=0.3)
plt.tight_layout(); plt.suptitle('coupled_oscillators_energy')
print("06_coupled_oscillators.py done")

plt.show()
