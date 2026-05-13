# -*- coding: utf-8 -*-
# 2.4 欧拉法解 ODE
# 使用欧拉方法求解常微分方程

import numpy as np
import matplotlib.pyplot as plt

def euler_method(f, y0, t_span, dt):
    t0, tf = t_span
    t = np.arange(t0, tf + dt, dt)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(len(t) - 1):
        y[i + 1] = y[i] + dt * f(t[i], y[i])
    return t, y

def f_decay(t, y):
    return -0.5 * y

def f_oscillation(t, y):
    return -np.sin(t)

print("=== 欧拉法: 放射性衰变 dy/dt = -0.5y, y(0)=100 ===")
t1, y1 = euler_method(f_decay, 100, (0, 10), 0.1)
t1_exact = np.linspace(0, 10, 200)
y1_exact = 100 * np.exp(-0.5 * t1_exact)
print(f"  t=10时, 数值解={y1[-1]:.4f}, 精确解={100*np.exp(-5):.4f}")

print("\n=== 欧拉法: 简谐振荡 dy/dt = -sin(t), y(0)=0 ===")
t2, y2 = euler_method(f_oscillation, 0, (0, 4 * np.pi), 0.1)
t2_exact = np.linspace(0, 4 * np.pi, 500)
y2_exact = np.cos(t2_exact) - 1
print(f"  t=4π时, 数值解={y2[-1]:.4f}, 精确解={np.cos(4*np.pi)-1:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
ax.plot(t1, y1, "b-", label="欧拉法 (dt=0.1)")
ax.plot(t1_exact, y1_exact, "r--", label="精确解")
ax.set_xlabel("时间 t")
ax.set_ylabel("y(t)")
ax.set_title("放射性衰变: dy/dt = -0.5y")
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(t2, y2, "b-", label="欧拉法 (dt=0.1)")
ax.plot(t2_exact, y2_exact, "r--", label="精确解")
ax.set_xlabel("时间 t")
ax.set_ylabel("y(t)")
ax.set_title("振荡方程: dy/dt = -sin(t)")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
