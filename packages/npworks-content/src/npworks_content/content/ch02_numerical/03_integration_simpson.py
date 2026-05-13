# -*- coding: utf-8 -*-
# 2.3 辛普森积分
# 使用辛普森法则计算数值积分

import numpy as np
import matplotlib.pyplot as plt

def simpson(f, a, b, n):
    if n % 2 != 0:
        n += 1
    x = np.linspace(a, b, n + 1)
    y = f(x)
    h = (b - a) / n
    integral = h / 3 * (y[0] + y[-1] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-2:2]))
    return integral, x, y

def f(x):
    return np.exp(-x ** 2)

a, b = -3, 3
exact = np.sqrt(np.pi) * 0.9999779095030014

print("=== 辛普森积分: ∫exp(-x²)dx from -3 to 3 ===")
print(f"精确值: {exact:.10f}\n")

print(f"{'N':>8} {'近似值':>14} {'误差':>14} {'相对误差':>14}")
print("-" * 54)

ns = [4, 8, 16, 32, 64, 128]
errors_trap = []
errors_simp = []

for n in ns:
    result_s, _, _ = simpson(f, a, b, n)
    error_s = abs(result_s - exact)
    errors_simp.append(error_s)

    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = f(x)
    result_t = h * (0.5 * y[0] + np.sum(y[1:-1]) + 0.5 * y[-1])
    errors_trap.append(abs(result_t - exact))

    print(f"{n:>8d} {result_s:>14.10f} {error_s:>14.2e} {error_s/exact:>14.2e}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

x_smooth = np.linspace(a, b, 200)
n_demo = 10
_, x_demo, y_demo = simpson(f, a, b, n_demo)
ax1.plot(x_smooth, f(x_smooth), "b-", label="exp(-x²)")
ax1.fill_between(x_smooth, f(x_smooth), alpha=0.2, color="green", label="精确积分区域")
ax1.plot(x_demo, y_demo, "ro-", markersize=4, label=f"辛普森 (N={n_demo})")
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.set_title("辛普森法则积分")
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.loglog(ns, errors_trap, "bo-", label="梯形法 O(h²)")
ax2.loglog(ns, errors_simp, "rs-", label="辛普森法 O(h⁴)")
ax2.set_xlabel("N (分割数)")
ax2.set_ylabel("绝对误差")
ax2.set_title("梯形法 vs 辛普森法 收敛性对比")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
