"""
Flow past a cylinder using the projection method with immersed boundary.
Solves 2D incompressible Navier-Stokes on a collocated grid.
Uses immersed boundary approach to enforce no-slip on the cylinder.
Saves vorticity field image.
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

Nx, Ny = 200, 100
Lx, Ly = 4.0, 2.0
dx = Lx / Nx
dy = Ly / Ny
cx, cy, R = 1.0, 1.0, 0.1
U_inf = 1.0
Re = 150.0
nu = U_inf * 2 * R / Re
rho = 1.0
dt = 0.002
nt = 20000

u = np.ones((Nx + 1, Ny + 1)) * U_inf
v = np.zeros((Nx + 1, Ny + 1))
p = np.zeros((Nx + 1, Ny + 1))

x = np.linspace(0, Lx, Nx + 1)
y = np.linspace(0, Ly, Ny + 1)
X, Y = np.meshgrid(x, y, indexing='ij')
mask = (X - cx)**2 + (Y - cy)**2 < R**2

u[mask] = 0.0
v[mask] = 0.0

# probe point (5R downstream of cylinder centre) for the shedding frequency
probe_i = int((cx + 5 * R) / dx)
probe_j = int(cy / dy)
v_probe = np.zeros(nt)

for n in range(nt):
    un = u.copy()
    vn = v.copy()

    # Advection + diffusion for u
    dudx = np.zeros_like(u)
    dudy = np.zeros_like(u)
    d2udx2 = np.zeros_like(u)
    d2udy2 = np.zeros_like(u)
    dudx[1:-1, :] = (u[2:, :] - u[:-2, :]) / (2 * dx)
    dudy[:, 1:-1] = (u[:, 2:] - u[:, :-2]) / (2 * dy)
    d2udx2[1:-1, :] = (u[2:, :] - 2 * u[1:-1, :] + u[:-2, :]) / dx**2
    d2udy2[:, 1:-1] = (u[:, 2:] - 2 * u[:, 1:-1] + u[:, :-2]) / dy**2

    u_star = un + dt * (-un * dudx - vn * dudy + nu * (d2udx2 + d2udy2))

    # Advection + diffusion for v
    dvdx = np.zeros_like(v)
    dvdy = np.zeros_like(v)
    d2vdx2 = np.zeros_like(v)
    d2vdy2 = np.zeros_like(v)
    dvdx[1:-1, :] = (v[2:, :] - v[:-2, :]) / (2 * dx)
    dvdy[:, 1:-1] = (v[:, 2:] - v[:, :-2]) / (2 * dy)
    d2vdx2[1:-1, :] = (v[2:, :] - 2 * v[1:-1, :] + v[:-2, :]) / dx**2
    d2vdy2[:, 1:-1] = (v[:, 2:] - 2 * v[:, 1:-1] + v[:, :-2]) / dy**2

    v_star = vn + dt * (-un * dvdx - vn * dvdy + nu * (d2vdx2 + d2vdy2))

    # Immersed boundary
    u_star[mask] = 0.0
    v_star[mask] = 0.0

    # Boundary conditions
    u_star[0, :] = U_inf
    u_star[-1, :] = u_star[-2, :]
    v_star[0, :] = 0.0
    v_star[-1, :] = v_star[-2, :]
    u_star[:, 0] = u_star[:, 1]
    u_star[:, -1] = u_star[:, -2]
    v_star[:, 0] = 0.0
    v_star[:, -1] = 0.0

    # Divergence
    div_us = np.zeros_like(p)
    div_us[1:-1, 1:-1] = (
        (u_star[2:, 1:-1] - u_star[:-2, 1:-1]) / (2 * dx)
        + (v_star[1:-1, 2:] - v_star[1:-1, :-2]) / (2 * dy))
    rhs = (rho / dt) * div_us

    # Pressure Poisson
    for _ in range(80):
        pn = p.copy()
        p[1:-1, 1:-1] = 0.25 * (
            pn[2:, 1:-1] + pn[:-2, 1:-1]
            + pn[1:-1, 2:] + pn[1:-1, :-2]
            - dx * dy * rhs[1:-1, 1:-1])
        p[0, :] = p[1, :]
        p[-1, :] = 0.0
        p[:, 0] = p[:, 1]
        p[:, -1] = p[:, -2]
        p[mask] = 0.0

    # Velocity correction
    u[1:-1, 1:-1] = u_star[1:-1, 1:-1] - (dt / rho) * (
        p[2:, 1:-1] - p[:-2, 1:-1]) / (2 * dx)
    v[1:-1, 1:-1] = v_star[1:-1, 1:-1] - (dt / rho) * (
        p[1:-1, 2:] - p[1:-1, :-2]) / (2 * dy)

    u[mask] = 0.0
    v[mask] = 0.0
    u[0, :] = U_inf
    v[0, :] = 0.0

    v_probe[n] = v[probe_i, probe_j]

    if n % 5000 == 0:
        print(f"Step {n}")

# Shedding frequency from the probe signal (discard the first half as transient)
half = nt // 2
signal = v_probe[half:] - v_probe[half:].mean()
freqs = np.fft.rfftfreq(nt - half, d=dt)
spectrum = np.abs(np.fft.rfft(signal))
f_shed = freqs[np.argmax(spectrum[1:]) + 1]
St = f_shed * 2 * R / U_inf
print(f"Shedding frequency f = {f_shed:.3f}, Strouhal number St = {St:.3f}")

# Vorticity
dudy_plot = np.zeros_like(u)
dvdx_plot = np.zeros_like(v)
dudy_plot[:, 1:-1] = (u[:, 2:] - u[:, :-2]) / (2 * dy)
dvdx_plot[1:-1, :] = (v[2:, :] - v[:-2, :]) / (2 * dx)
omega = dvdx_plot - dudy_plot

fig, ax = plt.subplots(1, 1, figsize=(12, 5))
diameter = 2 * R
cf = ax.contourf((X / diameter).T, (Y / diameter).T, omega.T,
                 levels=30, cmap='viridis', vmin=-10, vmax=10)
plt.colorbar(cf, ax=ax, label='vorticity (1/s)')
circle = plt.Circle((cx / diameter, cy / diameter), R / diameter,
                    color='gray', zorder=5)
ax.add_patch(circle)
ax.set_title(f'Vorticity Field (Re={Re:.0f})')
ax.set_xlabel('x/D')
ax.set_ylabel('y/D')
ax.set_aspect('equal')
plt.tight_layout()
plt.suptitle('cylinder_Re150')
plt.show()
