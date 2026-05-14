# -*- coding: utf-8 -*-
# 2.6 matplotlib 绘图
# 学习 matplotlib 基本绘图、子图和标注

import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 2 * np.pi, 100)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

ax = axes[0, 0]
ax.plot(x, np.sin(x), "b-", label="sin(x)", linewidth=2)
ax.plot(x, np.cos(x), "r--", label="cos(x)", linewidth=2)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("三角函数")
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0, 1]
x_exp = np.linspace(-2, 3, 100)
ax.plot(x_exp, np.exp(x_exp), "g-", label="exp(x)")
ax.plot(x_exp, np.log(np.maximum(x_exp, 0.01)), "m-", label="ln(x)")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("指数函数与对数函数")
ax.set_ylim(-5, 10)
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1, 0]
categories = ["力学", "电磁学", "热力学", "光学", "量子"]
values = [85, 72, 90, 68, 78]
colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7"]
bars = ax.bar(categories, values, color=colors)
ax.set_ylabel("分数")
ax.set_title("物理各科成绩")
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            str(val), ha="center", va="bottom")

ax = axes[1, 1]
np.random.seed(42)
x_data = np.random.randn(200)
y_data = 2 * x_data + np.random.randn(200) * 0.5
ax.scatter(x_data, y_data, alpha=0.5, s=10, c="blue")
coef = np.polyfit(x_data, y_data, 1)
x_fit = np.linspace(-3, 3, 100)
ax.plot(x_fit, np.polyval(coef, x_fit), "r-", linewidth=2,
        label=f"y = {coef[0]:.2f}x + {coef[1]:.2f}")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("散点图与线性回归")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
