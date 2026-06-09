"""
Lid-driven cavity flow using the projection method (Chorin's method).
Solves 2D incompressible Navier-Stokes equations.
Uses a collocated grid for simplicity, with a pressure Poisson equation.
Saves speed contour and streamlines.
"""
import numpy as np
import matplotlib.pyplot as plt

Nx, Ny = 64, 64
Lx, Ly = 1.0, 1.0
dx = Lx / Nx
dy = Ly / Ny
Re = 100.0
nu = 1.0 / Re
rho = 1.0
dt = 0.001
nt = 20000

u = np.zeros((Nx + 1, Ny + 1))
v = np.zeros((Nx + 1, Ny + 1))
p = np.zeros((Nx + 1, Ny + 1))

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

    # Velocity BCs on intermediate velocity
    u_star[0, :] = 0.0
    u_star[-1, :] = 1.0   # top lid
    u_star[:, 0] = 0.0
    u_star[:, -1] = 0.0
    v_star[0, :] = 0.0
    v_star[-1, :] = 0.0
    v_star[:, 0] = 0.0
    v_star[:, -1] = 0.0

    # Divergence of intermediate velocity
    div_us = np.zeros_like(p)
    div_us[1:-1, 1:-1] = (
        (u_star[2:, 1:-1] - u_star[:-2, 1:-1]) / (2 * dx)
        + (v_star[1:-1, 2:] - v_star[1:-1, :-2]) / (2 * dy))
    rhs = (rho / dt) * div_us

    # Pressure Poisson equation (Jacobi iteration)
    for _ in range(100):
        pn = p.copy()
        p[1:-1, 1:-1] = 0.25 * (
            pn[2:, 1:-1] + pn[:-2, 1:-1]
            + pn[1:-1, 2:] + pn[1:-1, :-2]
            - dx * dy * rhs[1:-1, 1:-1])
        p[0, :] = p[1, :]
        p[-1, :] = p[-2, :]
        p[:, 0] = p[:, 1]
        p[:, -1] = p[:, -2]

    # Velocity correction
    u[1:-1, 1:-1] = u_star[1:-1, 1:-1] - (dt / rho) * (
        p[2:, 1:-1] - p[:-2, 1:-1]) / (2 * dx)
    v[1:-1, 1:-1] = v_star[1:-1, 1:-1] - (dt / rho) * (
        p[1:-1, 2:] - p[1:-1, :-2]) / (2 * dy)

    # Velocity BCs
    u[0, :] = 0.0
    u[-1, :] = 1.0
    u[:, 0] = 0.0
    u[:, -1] = 0.0
    v[0, :] = 0.0
    v[-1, :] = 0.0
    v[:, 0] = 0.0
    v[:, -1] = 0.0

    if n % 5000 == 0:
        div_check = np.max(np.abs(
            (u[2:, 1:-1] - u[:-2, 1:-1]) / (2 * dx)
            + (v[1:-1, 2:] - v[1:-1, :-2]) / (2 * dy)))
        print(f"Step {n}, max|div(u)| = {div_check:.2e}")

x = np.linspace(0, Lx, Nx + 1)
y = np.linspace(0, Ly, Ny + 1)
X, Y = np.meshgrid(x, y, indexing='ij')

speed = np.sqrt(u**2 + v**2)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax1 = axes[0]
cf = ax1.contourf(X, Y, speed, levels=20, cmap='jet')
plt.colorbar(cf, ax=ax1)
ax1.set_title(f'Speed |u| (Re={Re:.0f})')
ax1.set_xlabel('x')
ax1.set_ylabel('y')
ax1.set_aspect('equal')

ax2 = axes[1]
ax2.streamplot(X.T, Y.T, u.T, v.T, density=2, linewidth=1, arrowsize=1)
ax2.set_title(f'Streamlines (Re={Re:.0f})')
ax2.set_xlabel('x')
ax2.set_ylabel('y')
ax2.set_aspect('equal')
plt.tight_layout()
fig.suptitle('cavity_Re100')
plt.show()

# Centerline velocity profiles
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))
mid_x = Nx // 2
mid_y = Ny // 2
axes2[0].plot(y, u[mid_x, :], 'b-', linewidth=2)
axes2[0].set_xlabel('y')
axes2[0].set_ylabel('u(y)')
axes2[0].set_title(f'u along vertical centerline (x=0.5)')
axes2[0].grid(True)

axes2[1].plot(x, v[:, mid_y], 'r-', linewidth=2)
axes2[1].set_xlabel('x')
axes2[1].set_ylabel('v(x)')
axes2[1].set_title(f'v along horizontal centerline (y=0.5)')
axes2[1].grid(True)
plt.tight_layout()
fig2.suptitle('cavity_centerline')
plt.show()
