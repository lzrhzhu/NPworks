# -*- coding: utf-8 -*-
# 2.2 梯形法积分
# 使用梯形法则计算数值积分

import numpy as np
import matplotlib.pyplot as plt

def trapezoidal(f, a, b, n):
    x = np.linspace(a, b, n + 1)
    y = f(x)
    h = (b - a) / n
    integral = h * (0.5 * y[0] + np.sum(y[1:-1]) + 0.5 * y[-1])
    return integral, x, y

def f(x):
    return np.sin(x)

a, b = 0, np.pi
exact = 2.0

print("=== 梯形法积分: ∫sin(x)dx from 0 to π ===")
print(f"精确值: {exact:.10f}\n")

print(f"{'N':>8} {'近似值':>14} {'误差':>14} {'相对误差':>14}")
print("-" * 54)

ns = [4, 8, 16, 32, 64, 128, 256, 512, 1024]
errors = []
for n in ns:
    result, _, _ = trapezoidal(f, a, b, n)
    error = abs(result - exact)
    rel_error = error / exact
    errors.append(error)
    print(f"{n:>8d} {result:>14.10f} {error:>14.2e} {rel_error:>14.2e}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

n_demo = 8
_, x_demo, y_demo = trapezoidal(f, a, b, n_demo)
x_smooth = np.linspace(a, b, 200)
ax1.plot(x_smooth, f(x_smooth), "b-", label="sin(x)")
ax1.fill_between(x_demo, y_demo, alpha=0.3, color="orange", label="梯形近似")
ax1.plot(x_demo, y_demo, "ro-", markersize=4)
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.set_title(f"梯形法积分 (N={n_demo})")
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.loglog(ns, errors, "ro-", label="实际误差")
ax2.loglog(ns, [errors[0] * (ns[0] / n) ** 2 for n in ns], "b--", label="O(h²) 参考线")
ax2.set_xlabel("N (分割数)")
ax2.set_ylabel("绝对误差")
ax2.set_title("梯形法收敛性分析")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
