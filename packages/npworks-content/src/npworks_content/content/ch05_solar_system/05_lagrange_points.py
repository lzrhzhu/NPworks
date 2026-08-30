import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

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
fig, ax = plt.subplots(figsize=(6.4, 4.8))
ax.plot(x1, 0, 'o', color='#E69F00', markersize=11, zorder=5)   # 主天体1
ax.plot(x2, 0, 'o', color='#0072B2', markersize=8, zorder=5)  # 主天体2
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
ax.set_xlabel(r'$x^*$')
ax.set_ylabel(r'$y^*$')
plt.tight_layout()
plt.suptitle('lagrange_points')


# ---------- 图2：地月系统 L2 附近的三维晕轨道（Halo orbit） ----------
# 采用正文给出的精确初值，完整积分三维 CR3BP 一个周期。
mu_h = 0.012150571430596
s0 = np.array([1.095345895545096, 0.0, 0.054906962886565,
               0.0, 0.246454099147264, 0.0])
T_period = 3.352409466028066


def deriv3d(_time, state):
    x, y, z, vx, vy, vz = state
    r1 = np.sqrt((x + mu_h) ** 2 + y ** 2 + z ** 2)
    r2 = np.sqrt((x - (1.0 - mu_h)) ** 2 + y ** 2 + z ** 2)
    ax_ = 2.0 * vy + x - (1.0 - mu_h) * (x + mu_h) / r1 ** 3 - mu_h * (x - (1.0 - mu_h)) / r2 ** 3
    ay_ = -2.0 * vx + y - (1.0 - mu_h) * y / r1 ** 3 - mu_h * y / r2 ** 3
    az_ = -(1.0 - mu_h) * z / r1 ** 3 - mu_h * z / r2 ** 3
    return np.array([vx, vy, vz, ax_, ay_, az_])


t_eval = np.linspace(0.0, T_period, 4001)
solution = solve_ivp(
    deriv3d,
    (0.0, T_period),
    s0,
    method='DOP853',
    dense_output=True,
    rtol=1e-10,
    atol=1e-12,
)
if not solution.success:
    raise RuntimeError(solution.message)
traj = solution.sol(t_eval).T
position_closure = np.linalg.norm(traj[-1, :3] - traj[0, :3])
state_closure = np.linalg.norm(traj[-1] - traj[0])

fig = plt.figure(figsize=(6.4, 5.4))
ax = fig.add_subplot(111, projection='3d')
ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], color='#0072B2', linestyle='-')
ax.plot([1.0 - mu_h], [0], [0], 'o', color='#D55E00', markersize=7)
ax.text(1.0 - mu_h, 0, 0.01, r'$P_2$')
ax.set_xlabel(r'$x^*$', labelpad=6)
ax.set_ylabel(r'$y^*$', labelpad=6)
ax.set_zlabel(r'$z^*$', labelpad=6)
for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
    axis.set_major_locator(MaxNLocator(4))
ax.set_box_aspect(np.ptp(traj[:, :3], axis=0))
ax.view_init(elev=22, azim=-58)
plt.tight_layout()
plt.suptitle('halo_orbit')

print(f'Halo orbit DOP853 accepted steps: {len(solution.t) - 1}')
print(f'Halo orbit function evaluations: {solution.nfev}')
print(f'Halo orbit position closure error: {position_closure:.6e}')
print(f'Halo orbit state closure error: {state_closure:.6e}')

plt.show()
