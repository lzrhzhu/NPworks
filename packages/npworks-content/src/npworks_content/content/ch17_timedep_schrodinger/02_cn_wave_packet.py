"""
Crank-Nicolson method for a Gaussian wave packet hitting a potential
barrier with E < V0 (genuine tunneling regime). Shows |psi|^2 at
several times. Uses hbar=1, m=1.

One step: solve  A psi^{n+1} = B psi^n  with sparse tridiagonal matrices
    A = I + i*dt*H/2,  B = I - i*dt*H/2.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
from scipy.sparse.linalg import factorized

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

x_min, x_max = -16.0, 16.0
N = 640
x = np.linspace(x_min, x_max, N)
dx = x[1] - x[0]
dt = 0.005
Nt = 500

V_height = 6.0        # barrier height above the mean energy E = 4.5
V_width = 0.8
V = np.zeros(N)
V[np.abs(x) < V_width / 2] = V_height

x0, sigma, k0 = -5.0, 2.0, 3.0          # E = k0^2/2 = 4.5 < V0 = 6
psi = (2 * np.pi * sigma ** 2) ** (-0.25) \
      * np.exp(-(x - x0) ** 2 / (4 * sigma ** 2)) * np.exp(1j * k0 * x)
psi /= np.sqrt(np.trapz(np.abs(psi) ** 2, x))

# Dirichlet boundaries are fixed at zero, so solve only for interior points.
# This preserves the Cayley-unitary update on the actual unknown vector.
M = N - 2
V_inner = V[1:-1]
alpha = 1j * dt / (4 * dx ** 2)          # hbar = m = 1
diag_main = 1 + 2 * alpha + 1j * dt / 2 * V_inner
diag_off = -alpha * np.ones(M - 1)
A = sparse.diags([diag_off, diag_main, diag_off], [-1, 0, 1], format='csc')
B = sparse.diags([alpha * np.ones(M - 1),
                  1 - 2 * alpha - 1j * dt / 2 * V_inner,
                  alpha * np.ones(M - 1)], [-1, 0, 1], format='csc')
solve_A = factorized(A)

psi[0] = 0
psi[-1] = 0
psi_inner = psi[1:-1].copy()

snap_steps = [0, 100, 200, 350, 500]
snapshots = [(0, np.abs(psi) ** 2)]
norms = [np.trapz(np.abs(psi) ** 2, x)]
for n in range(1, Nt + 1):
    psi_inner = solve_A(B @ psi_inner)
    psi[1:-1] = psi_inner
    psi[0] = 0
    psi[-1] = 0
    norms.append(np.trapz(np.abs(psi) ** 2, x))
    if n in snap_steps:
        snapshots.append((n, np.abs(psi) ** 2))

norm_err = max(abs(np.asarray(norms) - 1.0))
print(f"max |norm - 1| over all steps: {norm_err:.2e}")

colors = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
styles = ['-', '--', '-.', ':', '-.']

# --- Fig 1: wave packet evolution ---
fig, ax = plt.subplots(figsize=(7.2, 4.5))
peak0 = snapshots[0][1].max()
for idx, ((n, prob), color) in enumerate(zip(snapshots, colors)):
    ax.plot(x, prob, color=color, ls=styles[idx % len(styles)],
            label=f"t = {n * dt:.2f}")
ax.fill_between(x, 0, V / V_height * 0.5 * peak0, alpha=0.2,
                color='red', label='Barrier (scaled)')
ax.set_xlabel("x (a.u.)")
ax.set_ylabel(r"$|\psi|^2$ (a.u.$^{-1}$)")
ax.set_title("Crank-Nicolson: tunneling through barrier (E=4.5 < V0=6)")
ax.legend(frameon=False, fontsize=8)
ax.set_xlim(-12, 12)

fig.suptitle('cn_barrier')
plt.show()

# --- Fig 2: potential barrier ---
fig, ax = plt.subplots(figsize=(7.2, 2.8))
ax.fill_between(x, 0, V, alpha=0.4, color='orange')
ax.plot(x, V, 'k-', linewidth=1)
ax.set_xlabel("x (a.u.)")
ax.set_ylabel(r"$V(x)$ (a.u.)")
ax.set_title("Rectangular barrier: V0 = 6, width = 0.8")

fig.suptitle('cn_barrier_potential')
plt.show()
