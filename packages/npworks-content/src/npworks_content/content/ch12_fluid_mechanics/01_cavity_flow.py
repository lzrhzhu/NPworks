"""
Lid-driven cavity flow using the projection method (Chorin's method).
Solves 2D incompressible Navier-Stokes equations on a collocated grid.
Outputs: speed contour, streamlines, and two centerline velocity profiles.
"""
import numpy as np
import matplotlib.pyplot as plt
import os


def _img_dir(ch):
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(d, "markdown")):
            return os.path.join(d, "markdown", "images", ch)
        d = os.path.dirname(d)
    out = os.path.join(os.path.expanduser("~"), "npworks_figures", ch)
    os.makedirs(out, exist_ok=True)
    return out


IMG_DIR = _img_dir("ch12")

Nx, Ny = 64, 64
Lx, Ly = 1.0, 1.0
dx = Lx / Nx
dy = Ly / Ny
Re = 100.0
nu = 1.0 / Re
rho = 1.0
dt = 0.001
nt = 12000

u = np.zeros((Nx + 1, Ny + 1))
v = np.zeros((Nx + 1, Ny + 1))
p = np.zeros((Nx + 1, Ny + 1))

for n in range(nt):
    un = u.copy()
    vn = v.copy()

    dudx = np.zeros_like(u); dudy = np.zeros_like(u)
    d2udx2 = np.zeros_like(u); d2udy2 = np.zeros_like(u)
    dudx[1:-1, :] = (u[2:, :] - u[:-2, :]) / (2 * dx)
    dudy[:, 1:-1] = (u[:, 2:] - u[:, :-2]) / (2 * dy)
    d2udx2[1:-1, :] = (u[2:, :] - 2 * u[1:-1, :] + u[:-2, :]) / dx ** 2
    d2udy2[:, 1:-1] = (u[:, 2:] - 2 * u[:, 1:-1] + u[:, :-2]) / dy ** 2
    u_star = un + dt * (-un * dudx - vn * dudy + nu * (d2udx2 + d2udy2))

    dvdx = np.zeros_like(v); dvdy = np.zeros_like(v)
    d2vdx2 = np.zeros_like(v); d2vdy2 = np.zeros_like(v)
    dvdx[1:-1, :] = (v[2:, :] - v[:-2, :]) / (2 * dx)
    dvdy[:, 1:-1] = (v[:, 2:] - v[:, :-2]) / (2 * dy)
    d2vdx2[1:-1, :] = (v[2:, :] - 2 * v[1:-1, :] + v[:-2, :]) / dx ** 2
    d2vdy2[:, 1:-1] = (v[:, 2:] - 2 * v[:, 1:-1] + v[:, :-2]) / dy ** 2
    v_star = vn + dt * (-un * dvdx - vn * dvdy + nu * (d2vdx2 + d2vdy2))

    u_star[0, :] = 0.0; u_star[-1, :] = 1.0; u_star[:, 0] = 0.0; u_star[:, -1] = 0.0
    v_star[0, :] = 0.0; v_star[-1, :] = 0.0; v_star[:, 0] = 0.0; v_star[:, -1] = 0.0

    div_us = np.zeros_like(p)
    div_us[1:-1, 1:-1] = ((u_star[2:, 1:-1] - u_star[:-2, 1:-1]) / (2 * dx)
                          + (v_star[1:-1, 2:] - v_star[1:-1, :-2]) / (2 * dy))
    rhs = (rho / dt) * div_us

    for _ in range(100):
        pn = p.copy()
        p[1:-1, 1:-1] = 0.25 * (pn[2:, 1:-1] + pn[:-2, 1:-1]
                                + pn[1:-1, 2:] + pn[1:-1, :-2]
                                - dx * dy * rhs[1:-1, 1:-1])
        p[0, :] = p[1, :]; p[-1, :] = p[-2, :]; p[:, 0] = p[:, 1]; p[:, -1] = p[:, -2]

    u[1:-1, 1:-1] = u_star[1:-1, 1:-1] - (dt / rho) * (p[2:, 1:-1] - p[:-2, 1:-1]) / (2 * dx)
    v[1:-1, 1:-1] = v_star[1:-1, 1:-1] - (dt / rho) * (p[1:-1, 2:] - p[1:-1, :-2]) / (2 * dy)
    u[0, :] = 0.0; u[-1, :] = 1.0; u[:, 0] = 0.0; u[:, -1] = 0.0
    v[0, :] = 0.0; v[-1, :] = 0.0; v[:, 0] = 0.0; v[:, -1] = 0.0

x = np.linspace(0, Lx, Nx + 1)
y = np.linspace(0, Ly, Ny + 1)
X, Y = np.meshgrid(x, y, indexing='ij')
speed = np.sqrt(u ** 2 + v ** 2)
mid_x = Nx // 2
mid_y = Ny // 2

# --- 图1：速度大小 ---
fig, ax = plt.subplots(figsize=(6.5, 6))
cf = ax.contourf(X, Y, speed, levels=20, cmap='jet')
plt.colorbar(cf, ax=ax)
ax.set_title(f'Speed |u| (Re={Re:.0f})')
ax.set_xlabel('x'); ax.set_ylabel('y')
ax.set_aspect('equal')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch12_cavity_Re100.png"), dpi=130)
plt.close(fig)

# --- 图2：流线 ---
fig, ax = plt.subplots(figsize=(6.5, 6))
ax.streamplot(X.T, Y.T, u.T, v.T, density=2, linewidth=1, arrowsize=1)
ax.set_title(f'Streamlines (Re={Re:.0f})')
ax.set_xlabel('x'); ax.set_ylabel('y')
ax.set_aspect('equal')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch12_cavity_streamlines.png"), dpi=130)
plt.close(fig)

# --- 图3：竖直中心线 u(y) ---
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot(y, u[mid_x, :], 'b-', linewidth=2)
ax.set_xlabel('y'); ax.set_ylabel('u(y)')
ax.set_title('u along vertical centerline (x=0.5)')
ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch12_cavity_centerline.png"), dpi=130)
plt.close(fig)

# --- 图4：水平中心线 v(x) ---
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot(x, v[:, mid_y], 'r-', linewidth=2)
ax.set_xlabel('x'); ax.set_ylabel('v(x)')
ax.set_title('v along horizontal centerline (y=0.5)')
ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch12_cavity_centerline_v.png"), dpi=130)
plt.close(fig)

print("01_cavity_flow.py done")
