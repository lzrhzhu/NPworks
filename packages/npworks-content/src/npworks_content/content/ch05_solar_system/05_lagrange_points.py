import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
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


IMG_DIR = _img_dir("ch05")

mu = 0.012                     # 质量比（类地-月系统），便于看清各点分离
x1, x2 = -mu, 1.0 - mu         # 两主天体在旋转系中的位置


def collinear_f(x):
    r1 = abs(x + mu)
    r2 = abs(x - (1.0 - mu))
    return x - (1.0 - mu) * (x + mu) / r1 ** 3 - mu * (x - (1.0 - mu)) / r2 ** 3


# 三个共线点：L3(左)、L1(两体之间)、L2(右)
L3 = brentq(collinear_f, -2.0, x1 - 1e-4)
L1 = brentq(collinear_f, x1 + 1e-4, x2 - 1e-4)
L2 = brentq(collinear_f, x2 + 1e-4, 2.0)
L4 = (0.5 - mu, np.sqrt(3.0) / 2.0)
L5 = (0.5 - mu, -np.sqrt(3.0) / 2.0)

# ---------- 图1：旋转系中的五个拉格朗日点 ----------
fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(x1, 0, 'o', color='orange', markersize=18, zorder=5)   # 主天体1
ax.plot(x2, 0, 'o', color='dodgerblue', markersize=12, zorder=5)  # 主天体2
ax.text(x1, -0.13, r'$P_1$', ha='center')
ax.text(x2, -0.13, r'$P_2$', ha='center')
for name, xy in [('L1', (L1, 0)), ('L2', (L2, 0)), ('L3', (L3, 0)),
                 ('L4', L4), ('L5', L5)]:
    ax.plot(xy[0], xy[1], 'kx', markersize=9, mew=2, zorder=6)
    dy = 0.07 if name in ('L1', 'L2') else 0.0
    dy = -0.1 if name == 'L3' else dy
    ax.annotate(name, xy=xy, xytext=(xy[0] + 0.05, xy[1] + dy + 0.04),
                fontsize=11)
# 等边三角形辅助线（L4,L5）
tri = plt.Polygon([(x1, 0), (x2, 0), L4], fill=False, ls='--', color='gray',
                  alpha=0.6)
ax.add_patch(tri)
ax.set_aspect('equal')
ax.set_xlim(-1.6, 1.6)
ax.set_ylim(-1.1, 1.1)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Five Lagrange Points in the Rotating Frame')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch05_lagrange_points.png"), dpi=130)
plt.close(fig)


# ---------- 图2：地月系统 L2 附近的三维晕轨道（Halo orbit） ----------
# 采用正文给出的精确初值，完整积分三维 CR3BP 一个周期。
mu_h = 0.012150571430596
s0 = np.array([1.095345895545096, 0.0, 0.054906962886565,
               0.0, 0.246454099147264, 0.0])
T_period = 3.352409466028066


def deriv3d(state):
    x, y, z, vx, vy, vz = state
    r1 = np.sqrt((x + mu_h) ** 2 + y ** 2 + z ** 2)
    r2 = np.sqrt((x - (1.0 - mu_h)) ** 2 + y ** 2 + z ** 2)
    ax_ = 2.0 * vy + x - (1.0 - mu_h) * (x + mu_h) / r1 ** 3 - mu_h * (x - (1.0 - mu_h)) / r2 ** 3
    ay_ = -2.0 * vx + y - (1.0 - mu_h) * y / r1 ** 3 - mu_h * y / r2 ** 3
    az_ = -(1.0 - mu_h) * z / r1 ** 3 - mu_h * z / r2 ** 3
    return np.array([vx, vy, vz, ax_, ay_, az_])


dt = T_period / 4000.0
st = s0.copy()
traj = [st.copy()]
for _ in range(int(T_period / dt)):
    k1 = deriv3d(st)
    k2 = deriv3d(st + 0.5 * dt * k1)
    k3 = deriv3d(st + 0.5 * dt * k2)
    k4 = deriv3d(st + dt * k3)
    st = st + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    traj.append(st.copy())
traj = np.array(traj)

fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 'b-', linewidth=0.7)
ax.plot([1.0 - mu_h], [0], [0], 'o', color='dodgerblue', markersize=8)
ax.text(1.0 - mu_h, 0, 0.01, r'$P_2$')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.set_title('Halo Orbit around L2 (Earth-Moon system)')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch05_halo_orbit.png"), dpi=130)
plt.close(fig)

print("05_lagrange_points.py done")
