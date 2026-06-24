"""
Leapfrog (CTCS) method for free-particle Gaussian wave packet.
Shows |psi|^2 at different times.
Uses hbar=1, m=1.
"""
import numpy as np
import matplotlib.pyplot as plt

hbar = 1.0
m = 1.0

x_min, x_max = -20.0, 20.0
N = 400
x = np.linspace(x_min, x_max, N)
dx = x[1] - x[0]

dt = 0.5 * dx ** 2 * m / hbar * 0.9
Nt = 600

x0 = -5.0
sigma = 1.0
k0 = 3.0

psi = (2 * np.pi * sigma ** 2) ** (-0.25) \
      * np.exp(-(x - x0) ** 2 / (4 * sigma ** 2)) \
      * np.exp(1j * k0 * x)

norm = np.sqrt(np.trapz(np.abs(psi) ** 2, x))
psi = psi / norm

u = np.real(psi)
v = np.imag(psi)

Hu = np.zeros(N)
Hv = np.zeros(N)

def apply_H(f, V_arr):
    Hf = np.zeros_like(f)
    Hf[1:-1] = -0.5 * (f[2:] - 2 * f[1:-1] + f[:-2]) / dx ** 2 + V_arr[1:-1] * f[1:-1]
    return Hf

V = np.zeros(N)

Hu = apply_H(u, V)
v = v - 0.5 * dt / hbar * Hu

snap_times = [0, 150, 350, 600]
snapshots = []

psi_init = u + 1j * (v + 0.5 * dt / hbar * apply_H(u, V))
snapshots.append((0, np.abs(u + 1j * v) ** 2))

for n in range(1, Nt + 1):
    Hu = apply_H(u, V)
    v = v - dt / hbar * Hu
    Hv = apply_H(v, V)
    u = u + dt / hbar * Hv
    u[0] = 0
    u[-1] = 0
    v[0] = 0
    v[-1] = 0
    if n in snap_times:
        prob = u ** 2 + v ** 2
        snapshots.append((n, prob.copy()))

fig, ax = plt.subplots(figsize=(10, 6))
colors = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
for (n, prob), color in zip(snapshots, colors):
    t_val = n * dt
    ax.plot(x, prob, color=color, label=f"t = {t_val:.2f}")
ax.set_xlabel("x")
ax.set_ylabel("|psi|^2")
ax.set_title("Leapfrog: Free Gaussian Wave Packet (hbar=1, m=1, k0=3)")
ax.legend()
ax.grid(True)
ax.set_xlim(-15, 20)

fig.suptitle('leapfrog_free')
plt.show()
