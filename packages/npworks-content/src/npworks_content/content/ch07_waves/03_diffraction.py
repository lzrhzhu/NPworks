# -*- coding: utf-8 -*-
# 7.3 衍射
# 单缝衍射和圆孔衍射模拟

import numpy as np
import matplotlib.pyplot as plt

wavelength = 0.5
screen_distance = 20.0

print("=== 单缝衍射模拟 ===")

slit_widths = [0.5, 1.0, 2.0, 4.0]
y = np.linspace(-20, 20, 1000)

def single_slit_pattern(y, a, wavelength, L):
    theta = np.arctan(y / L)
    beta = np.pi * a * np.sin(theta) / wavelength
    I = np.where(np.abs(beta) < 1e-10, 1.0, (np.sin(beta) / beta) ** 2)
    return I

print(f"{'缝宽 a':>10} {'中央极大宽度':>14}")
print("-" * 26)
for a in slit_widths:
    central_width = 2 * wavelength * screen_distance / a
    print(f"{a:>10.1f} {central_width:>14.2f}")

print("\n=== 圆孔衍射 (艾里斑) ===")
D = 2.0
theta_screen = np.linspace(-5, 5, 500)
R, Theta = np.meshgrid(theta_screen, theta_screen)
r = np.sqrt(R ** 2 + Theta ** 2)
r_rad = np.radians(r)

x_airy = np.pi * D * np.sin(r_rad / 50) / wavelength
I_airy = np.where(np.abs(x_airy) < 1e-10, 1.0, (2 * np.ones_like(x_airy)))

from scipy.special import j1
x_airy = np.pi * D * np.tan(r_rad / 50) / wavelength
I_airy = np.where(np.abs(x_airy) < 1e-10, 1.0, (2 * j1(x_airy) / x_airy) ** 2)

airy_radius = 1.22 * wavelength / D
print(f"圆孔直径 D = {D}")
print(f"艾里斑角半径 θ = 1.22λ/D = {airy_radius:.4f} rad")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

ax = axes[0, 0]
for a in slit_widths:
    I = single_slit_pattern(y, a, wavelength, screen_distance)
    ax.plot(y, I, label=f"a={a}")
ax.set_xlabel("屏上位置 y")
ax.set_ylabel("归一化强度")
ax.set_title("单缝衍射: 不同缝宽")
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0, 1]
a_demo = 2.0
I_demo = single_slit_pattern(y, a_demo, wavelength, screen_distance)
theta_demo = np.arctan(y / screen_distance)

ax.plot(np.degrees(theta_demo) * 60, I_demo, "b-", linewidth=1.5)
ax.set_xlabel("衍射角 (角分)")
ax.set_ylabel("归一化强度")
ax.set_title(f"单缝衍射 (a={a_demo}, λ={wavelength})")
ax.grid(True, alpha=0.3)

minima_angles = [n * wavelength / a_demo for n in range(1, 4)]
for n, angle in enumerate(minima_angles, 1):
    y_min = screen_distance * np.tan(angle)
    ax.axvline(x=np.degrees(angle) * 60, color="red", linestyle=":", alpha=0.3)
    ax.text(np.degrees(angle) * 60, 0.5, f"n={n}", fontsize=8, color="red")

ax = axes[1, 0]
im = ax.imshow(I_airy, cmap="hot", extent=[theta_screen[0], theta_screen[-1],
                                              theta_screen[0], theta_screen[-1]])
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title(f"圆孔衍射 (艾里斑, D={D})")
plt.colorbar(im, ax=ax, label="强度")

ax = axes[1, 1]
r_line = np.linspace(0, 5, 500)
x_line = np.pi * D * np.radians(r_line / 50) / wavelength
I_line = np.where(np.abs(x_line) < 1e-10, 1.0, (2 * j1(x_line) / x_line) ** 2)
ax.plot(r_line, I_line, "b-", linewidth=2)
ax.set_xlabel("角位置 (任意单位)")
ax.set_ylabel("归一化强度")
ax.set_title("圆孔衍射: 径向强度分布")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
