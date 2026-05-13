# -*- coding: utf-8 -*-
# 6.1 波函数
# 平面波与波包

import numpy as np
import matplotlib.pyplot as plt

hbar = 1.0
m = 1.0

x = np.linspace(-20, 20, 1000)

def plane_wave(x, k, omega, t=0):
    return np.exp(1j * (k * x - omega * t))

def gaussian_wavepacket(x, x0, sigma, k0, t=0):
    sigma_t = sigma * np.sqrt(1 + (hbar * t / (2 * m * sigma ** 2)) ** 2)
    k = k0
    omega = hbar * k ** 2 / (2 * m)
    psi = (2 * np.pi * sigma_t ** 2) ** (-0.25) * \
          np.exp(-(x - x0 - hbar * k * t / m) ** 2 / (4 * sigma_t ** 2)) * \
          np.exp(1j * (k * x - omega * t))
    return psi

print("=== 波函数模拟 ===")

k0 = 2.0
omega = hbar * k0 ** 2 / (2 * m)
print(f"波数 k = {k0}")
print(f"角频率 ω = {omega:.4f}")
print(f"波长 λ = {2*np.pi/k0:.4f}")
print(f"频率 f = {omega/(2*np.pi):.4f}")

psi = plane_wave(x, k0, omega)
prob = np.abs(psi) ** 2

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax = axes[0, 0]
ax.plot(x, np.real(psi), "b-", label="Re(ψ)")
ax.plot(x, np.imag(psi), "r-", label="Im(ψ)")
ax.plot(x, prob, "k--", label="|ψ|²")
ax.set_xlabel("x")
ax.set_ylabel("ψ")
ax.set_title(f"平面波: ψ = exp(ikx), k={k0}")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(-10, 10)

ax = axes[0, 1]
for k_val in [1, 2, 4]:
    psi_k = plane_wave(x, k_val, hbar * k_val ** 2 / (2 * m))
    ax.plot(x, np.real(psi_k), label=f"k={k_val}, λ={2*np.pi/k_val:.2f}")
ax.set_xlabel("x")
ax.set_ylabel("Re(ψ)")
ax.set_title("不同波数的平面波")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(-10, 10)

ax = axes[1, 0]
x0 = -5.0
sigma = 1.0
times = [0, 1, 2, 3, 5]
for t in times:
    psi_wp = gaussian_wavepacket(x, x0, sigma, k0, t)
    ax.plot(x, np.abs(psi_wp) ** 2, label=f"t={t}")
ax.set_xlabel("x")
ax.set_ylabel("|ψ|²")
ax.set_title(f"高斯波包演化 (k₀={k0}, σ={sigma})")
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1, 1]
psi_t0 = gaussian_wavepacket(x, x0, sigma, k0, t=0)
dk = 0.05
k_array = np.arange(k0 - 3, k0 + 3, dk)
N_k = len(k_array)
psi_super = np.zeros(len(x), dtype=complex)
for ki in k_array:
    psi_super += plane_wave(x, ki, hbar * ki ** 2 / (2 * m)) * np.exp(-(ki - k0) ** 2 * sigma ** 2) * dk
psi_super /= np.sqrt(np.sum(np.abs(psi_super) ** 2) * (x[1] - x[0]))

ax.plot(x, np.abs(psi_t0) ** 2, "b-", linewidth=2, label="高斯波包 |ψ|²")
ax.plot(x, np.abs(psi_super) ** 2, "r--", linewidth=1.5, label="叠加态 |ψ|²")
ax.set_xlabel("x")
ax.set_ylabel("|ψ|²")
ax.set_title("波包 = 平面波的叠加")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
