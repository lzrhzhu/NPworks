"""等离子体振荡（Langmuir 振荡）。

把一团冷电子整体相对静止离子平移 x0，边界面电荷产生恢复电场，
电子做集体振荡，频率为等离子体频率
  omega_p = sqrt(n e^2 / (eps0 m))
（归一化单位下 omega_p = 1）。振荡 x(t) = x0 cos(omega_p t)，
周期是电子集体响应的最快时间尺度。
"""
import numpy as np
import matplotlib.pyplot as plt

omega_p = 1.0
x0 = 0.3
T = 4 * 2 * np.pi / omega_p      # 4 个周期
N = 2000
t = np.linspace(0, T, N)
x = x0 * np.cos(omega_p * t)     # 解析：x'' = -omega_p^2 x

# 数值验证（速度 Verlet）
dt = T / N
xn, vn = x0, 0.0
x_num = []
for _ in range(N):
    vn += 0.5 * (-omega_p ** 2 * xn) * dt
    xn += vn * dt
    vn += 0.5 * (-omega_p ** 2 * xn) * dt
    x_num.append(xn)
x_num = np.array(x_num)

# FFT：应峰值在 omega_p
xs = x - x.mean()
freq = np.fft.rfftfreq(N, d=T / N) * (2 * np.pi)   # 角频率
spec = np.abs(np.fft.rfft(xs))

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

axes[0].plot(t, x, 'b-', linewidth=2, label='解析 $x_0\\cos(\\omega_p t)$')
axes[0].plot(t, x_num, 'r--', linewidth=1.5, label='数值（Verlet）')
axes[0].set_xlabel('time $t$')
axes[0].set_ylabel('位移 $x$')
axes[0].set_title(r'集体振荡：频率 $\omega_p$')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(freq, spec, 'g-', linewidth=1.8)
pk = freq[np.argmax(spec)]
axes[1].axvline(omega_p, color='r', linestyle='--', linewidth=2,
                label=fr'谱峰 $\omega={pk:.2f}\approx\omega_p=1$')
axes[1].set_xlim(0, 3)
axes[1].set_xlabel(r'角频率 $\omega$')
axes[1].set_ylabel('振幅谱')
axes[1].set_title('FFT：单一集体频率 ω_p')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('plasma_oscillation')
plt.show()
print("02_plasma_oscillation.py done")
