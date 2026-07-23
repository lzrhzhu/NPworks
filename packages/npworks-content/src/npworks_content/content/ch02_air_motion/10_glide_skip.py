import math
import matplotlib.pyplot as plt

# 物理常量与指数大气模型
g = 9.8
rho0 = 1.29
H = 8500.0

# 初始条件：在大气层上缘（约 60 km，气动开始显著处）以水平高超音速飞行
v0 = 4000.0          # 初速 (m/s)
y0 = 60000.0         # 初始高度 (m)，约 60 km
gamma_deg = 0.0      # 初始飞行轨迹角（水平）
dt = 0.05

CD_A_m = 1.0e-3      # C_D·A/m (m^-1)，弹道系数 beta = m/(C_D*A) ~ 1000 kg/m^2（典型滑翔飞行器）
Emax = 2.5           # 最大升阻比（高超声速典型值）

MAX_RANGE = 1.5e7    # 15000 km
MAX_STEPS = 600000


def density(y):
    if y < 0:
        y = 0.0
    return rho0 * math.exp(-y / H)


def accel(x, y, vx, vy, cL_A_m):
    v = math.sqrt(vx * vx + vy * vy)
    rho = density(y)
    f_D = 0.5 * rho * CD_A_m * v
    f_L = 0.5 * rho * cL_A_m * v
    ax = -f_D * vx - f_L * vy
    ay = -g - f_D * vy + f_L * vx
    return ax, ay


def simulate(mode):
    gr = gamma_deg * math.pi / 180.0
    vx = v0 * math.cos(gr)
    vy = -v0 * math.sin(gr)
    x, y = 0.0, y0
    xs, ys = [x], [y]
    n = 0
    while y >= 0 and (vx * vx + vy * vy) > 2500 and n < MAX_STEPS and x < MAX_RANGE:
        if mode == 'glide':
            # 平衡滑翔（钱学森）：主动调节升力使其托住重力（L ≈ mg），
            # 不超过最大升力——这正是"靠控制维持滑翔"的体现。
            v = math.sqrt(vx * vx + vy * vy)
            rho = density(y)
            cL_A_m = min(CD_A_m * Emax, 2.0 * g / (rho * v * v + 1e-30))
        elif mode == 'skip':
            # 跳跃弹道（Sänger）：固定使用最大升阻比，被动弹道。
            cL_A_m = CD_A_m * Emax
        else:
            # 纯弹道：无升力，仅阻力。
            cL_A_m = 0.0
        ax, ay = accel(x, y, vx, vy, cL_A_m)
        vx = vx + ax * dt
        vy = vy + ay * dt
        x = x + vx * dt
        y = y + vy * dt
        xs.append(x)
        ys.append(y)
        n += 1
    return xs, ys


modes = [
    ('ballistic', 'Ballistic (E=0)'),
    ('glide', 'Equilibrium glide (Qian, lift = weight)'),
    ('skip', 'Skip-glide (Sanger, E=%.1f)' % Emax),
]

plt.figure(figsize=(11, 6))

for mode, label_text in modes:
    xs, ys = simulate(mode)
    plt.plot([xi / 1000.0 for xi in xs], [yi / 1000.0 for yi in ys],
             label='%s (range=%.0f km)' % (label_text, xs[-1] / 1000.0))

plt.axhline(0, color='black', linewidth=0.8)
plt.xlabel('Downrange (km)')
plt.ylabel('Altitude (km)')
plt.title('Boost-Glide vs Skip Trajectories (Lift + Drag, Exponential Atmosphere)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('glide_skip')
plt.show()
print("10_glide_skip.py done")
