"""
Flow past a cylinder using the projection method with immersed boundary.
Solves 2D incompressible Navier-Stokes on a collocated grid.
Uses immersed boundary approach to enforce no-slip on the cylinder.
Saves vorticity field image.
"""
import numpy as np
import matplotlib.pyplot as plt

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

    if n % 5000 == 0:
        print(f"Step {n}")

# Vorticity
dudy_plot = np.zeros_like(u)
dvdx_plot = np.zeros_like(v)
dudy_plot[:, 1:-1] = (u[:, 2:] - u[:, :-2]) / (2 * dy)
dvdx_plot[1:-1, :] = (v[2:, :] - v[:-2, :]) / (2 * dx)
omega = dvdx_plot - dudy_plot

fig, ax = plt.subplots(1, 1, figsize=(12, 5))
cf = ax.contourf(X.T, Y.T, omega.T, levels=30, cmap='RdBu_r', vmin=-10, vmax=10)
plt.colorbar(cf, ax=ax, label='Vorticity')
circle = plt.Circle((cx, cy), R, color='gray', zorder=5)
ax.add_patch(circle)
ax.set_title(f'Vorticity Field (Re={Re:.0f})')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_aspect('equal')
plt.tight_layout()
plt.suptitle('cylinder_Re150')
plt.show()
