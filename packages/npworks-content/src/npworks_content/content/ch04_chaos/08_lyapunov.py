import numpy as np
import matplotlib.pyplot as plt
import math


g = 9.8
l = 9.8
Omega2 = g / l
q = 0.5
Omega_D = 2.0 / 3.0
T_D = 2 * np.pi / Omega_D
dt = 0.01
steps_per_T = int(round(T_D / dt))
dt = T_D / steps_per_T          # 修正 dt，使其精确整除驱动周期
d0 = 1e-9                       # 重正化后的偏移距离


def rk4_step(th, om, t, dt, FD):
    # RK4 单步：状态 (theta, omega)，标量运算以提高速度
    k1t = om
    k1o = -Omega2 * math.sin(th) - q * om + FD * math.sin(Omega_D * t)
    th2 = th + 0.5 * dt * k1t
    om2 = om + 0.5 * dt * k1o
    k2t = om2
    k2o = -Omega2 * math.sin(th2) - q * om2 + FD * math.sin(Omega_D * (t + 0.5 * dt))
    th3 = th + 0.5 * dt * k2t
    om3 = om + 0.5 * dt * k2o
    k3t = om3
    k3o = -Omega2 * math.sin(th3) - q * om3 + FD * math.sin(Omega_D * (t + 0.5 * dt))
    th4 = th + dt * k3t
    om4 = om + dt * k3o
    k4t = om4
    k4o = -Omega2 * math.sin(th4) - q * om4 + FD * math.sin(Omega_D * (t + dt))
    th_new = th + (dt / 6.0) * (k1t + 2 * k2t + 2 * k3t + k4t)
    om_new = om + (dt / 6.0) * (k1o + 2 * k2o + 2 * k3o + k4o)
    return th_new, om_new


def compute_lyapunov(FD, theta0=0.2, omega0=0.0, n_relay=100, N=800):
    """重正化法计算最大 Lyapunov 指数。

    n_relay: 丢弃的暂态驱动周期数；N: 累计统计的驱动周期数。
    """
    th1 = theta0
    om1 = omega0
    th2 = theta0 + d0          # 邻近轨道：初始偏移 d0
    om2 = omega0
    t = 0.0

    # 暂态阶段：同步积分并持续重正化，等参考轨道弛豫到吸引子上
    for n in range(n_relay):
        for j in range(steps_per_T):
            th1, om1 = rk4_step(th1, om1, t, dt, FD)
            th2, om2 = rk4_step(th2, om2, t, dt, FD)
            t += dt
        dth = th2 - th1
        dom = om2 - om1
        d = math.hypot(dth, dom)
        if d > 0:
            th2 = th1 + d0 * dth / d
            om2 = om1 + d0 * dom / d

    # 统计阶段：每周期记录 ln(d_i/d_0) 并重正化
    lam_sum = 0.0
    for n in range(N):
        for j in range(steps_per_T):
            th1, om1 = rk4_step(th1, om1, t, dt, FD)
            th2, om2 = rk4_step(th2, om2, t, dt, FD)
            t += dt
        dth = th2 - th1
        dom = om2 - om1
        d = math.hypot(dth, dom)
        lam_sum += math.log(d / d0)
        th2 = th1 + d0 * dth / d
        om2 = om1 + d0 * dom / d

    return lam_sum / (N * T_D)


# 两点诊断：弱驱动（周期运动）与强驱动（混沌）
for FD in [0.5, 1.2]:
    lam = compute_lyapunov(FD)
    print("FD = {:.1f}: lambda = {:+.4f} {}".format(
        FD, lam, "(chaotic)" if lam > 0 else "(stable)"))

# 扫描 F_D in [1.30, 1.50]：周期倍增级联与混沌带
FD_values = np.round(np.arange(1.30, 1.5001, 0.004), 4)
lam_values = []
for FD in FD_values:
    lam = compute_lyapunov(FD, n_relay=50, N=400)
    lam_values.append(lam)

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(FD_values, lam_values, 'b.-', markersize=3, linewidth=0.7)
ax.axhline(0.0, color='k', linewidth=0.8)
ax.set_xlabel(r'$F_D$')
ax.set_ylabel(r'$\lambda$')
ax.set_title(r'Lyapunov Exponent vs $F_D$')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('lyapunov_scan')
print("08_lyapunov.py done")

plt.show()
