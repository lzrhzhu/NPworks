"""
Leapfrog (CTCS) method for free-particle Gaussian wave packet.
Shows |psi|^2 at different times. Uses hbar=1, m=1.

Textbook consistency: backward half-step start
    v^{-1/2} = v^0 + (dt / (2*hbar)) * H u^0
then alternating updates
    v^{n+1/2} = v^{n-1/2} - (dt/hbar) * H u^n
    u^{n+1}   = u^n   + (dt/hbar) * H v^{n+1/2}
Snapshots at integer layers use the half-step average
    v^n ~ (v^{n+1/2} + v^{n-1/2}) / 2.
"""
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300,
    'figure.figsize': (6.4, 4.0),
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'axes.grid': False,
    'axes.unicode_minus': False,
})

hbar = 1.0
m = 1.0

x_min, x_max = -20.0, 20.0
N = 400
x = np.linspace(x_min, x_max, N)
dx = x[1] - x[0]

dt = 0.45 * dx ** 2 * m / hbar      # below stability bound dt <= dx^2 (hbar=m=1)
Nt = 600

x0 = -5.0
sigma = 1.0
k0 = 3.0

psi = (2 * np.pi * sigma ** 2) ** (-0.25) \
      * np.exp(-(x - x0) ** 2 / (4 * sigma ** 2)) \
      * np.exp(1j * k0 * x)
psi /= np.sqrt(np.trapz(np.abs(psi) ** 2, x))

u = psi.real
v0 = psi.imag

V = np.zeros(N)


def apply_H(f, V_arr):
    """Discrete Hamiltonian action: central difference + potential."""
    Hf = np.zeros_like(f)
    Hf[1:-1] = -0.5 * (f[2:] - 2 * f[1:-1] + f[:-2]) / dx ** 2 \
               + V_arr[1:-1] * f[1:-1]
    return Hf


# half-step start: backward value v^{-1/2} = v^0 + (dt/(2*hbar)) * H u^0
v = v0 + 0.5 * dt / hbar * apply_H(u, V)

snap_steps = [0, 150, 350, 600]
snapshots = [(0, u ** 2 + v0 ** 2)]          # t=0 uses u^0, v^0
norms = [np.sum(u ** 2 + v0 ** 2) * dx]

for n in range(1, Nt + 1):
    Hu = apply_H(u, V)
    v_new = v - dt / hbar * Hu               # v^{n+1/2}
    Hv = apply_H(v_new, V)
    u = u + dt / hbar * Hv                   # u^{n+1}
    u[0] = 0; u[-1] = 0                      # Dirichlet boundary
    v_new[0] = 0; v_new[-1] = 0
    if n in snap_steps:
        v_int = 0.5 * (v_new + v)            # integer-layer reconstruction
        prob = u ** 2 + v_int ** 2
        snapshots.append((n, prob))
        norms.append(np.sum(prob) * dx)
    v = v_new

print(f"leapfrog norm drift: max |N(t)-1| = {max(abs(np.array(norms) - 1)):.2e}")

fig, ax = plt.subplots(figsize=(7.2, 4.5))
colors = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
styles = ['-', '--', '-.', ':']
for idx, ((n, prob), color) in enumerate(zip(snapshots, colors)):
    ax.plot(x, prob, color=color, ls=styles[idx % len(styles)],
            label=f"t = {n * dt:.2f}")
ax.set_xlabel("x (a.u.)")
ax.set_ylabel(r"$|\psi|^2$ (a.u.$^{-1}$)")
ax.set_title("Leapfrog: free Gaussian wave packet (E = k0^2/2 = 4.5)")
ax.legend(frameon=False)
ax.set_xlim(-15, 20)

fig.suptitle('leapfrog_free')
plt.show()
