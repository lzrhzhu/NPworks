# -*- coding: utf-8 -*-
# 7.2 干涉
# 双缝干涉模拟

import numpy as np
import matplotlib.pyplot as plt

wavelength = 0.5
k = 2 * np.pi / wavelength
screen_distance = 20.0
slit_separation = 3.0
slit_width = 0.3

print("=== 双缝干涉模拟 ===")
print(f"波长 λ = {wavelength}")
print(f"缝间距 d = {slit_separation}")
print(f"缝宽 a = {slit_width}")
print(f"屏距 L = {screen_distance}")

y = np.linspace(-15, 15, 1000)

theta = np.arctan(y / screen_distance)

alpha = np.pi * slit_separation * np.sin(theta) / wavelength
I_interference = np.cos(alpha) ** 2

beta = np.pi * slit_width * np.sin(theta) / wavelength
I_diffraction = np.where(np.abs(beta) < 1e-10, 1.0, (np.sin(beta) / beta) ** 2)

I_total = I_interference * I_diffraction
I_total /= I_total.max()

x_2d = np.linspace(-5, 5, 200)
y_2d = np.linspace(-15, 15, 200)
X2, Y2 = np.meshgrid(x_2d, y_2d)
theta_2d = np.arctan(Y2 / screen_distance)
alpha_2d = np.pi * slit_separation * np.sin(theta_2d) / wavelength
beta_2d = np.pi * slit_width * np.sin(theta_2d) / wavelength
I_interf_2d = np.cos(alpha_2d) ** 2
I_diff_2d = np.where(np.abs(beta_2d) < 1e-10, 1.0, (np.sin(beta_2d) / beta_2d) ** 2)
I_2d = I_interf_2d * I_diff_2d

fringe_spacing = wavelength * screen_distance / slit_separation
print(f"\n条纹间距 Δy = λL/d = {fringe_spacing:.2f}")

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

ax1.plot(y, I_interference, "b-", label="双缝干涉", alpha=0.7)
ax1.plot(y, I_diffraction, "r--", label="单缝衍射包络", alpha=0.7)
ax1.plot(y, I_total, "k-", linewidth=1.5, label="总强度")
ax1.set_xlabel("屏上位置 y")
ax1.set_ylabel("归一化强度")
ax1.set_title("双缝干涉强度分布")
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.imshow(I_2d, cmap="hot", aspect="auto", origin="lower",
           extent=[x_2d[0], x_2d[-1], y_2d[0], y_2d[-1]])
ax2.set_xlabel("x")
ax2.set_ylabel("y")
ax2.set_title("干涉条纹 (二维)")

for d_val in [1.5, 3.0, 6.0]:
    alpha_v = np.pi * d_val * np.sin(theta) / wavelength
    I_v = np.cos(alpha_v) ** 2
    ax3.plot(y, I_v, label=f"d={d_val}, Δy={wavelength*screen_distance/d_val:.2f}")

ax3.set_xlabel("屏上位置 y")
ax3.set_ylabel("归一化强度")
ax3.set_title("不同缝间距的干涉图样")
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
