# -*- coding: utf-8 -*-
# 4.2 磁场
# 电流产生的磁场 (毕奥-萨伐尔定律)

import numpy as np
import matplotlib.pyplot as plt

mu0 = 4 * np.pi * 1e-7

def magnetic_field_wire(x, y, wire_pos, I):
    wx, wy = wire_pos
    dx = x - wx
    dy = y - wy
    r2 = dx ** 2 + dy ** 2
    r2 = np.maximum(r2, 0.01)
    Bx = -mu0 * I * dy / (2 * np.pi * r2)
    By = mu0 * I * dx / (2 * np.pi * r2)
    return Bx, By

def total_B(x, y, wires):
    Bx_total = np.zeros_like(x, dtype=float)
    By_total = np.zeros_like(y, dtype=float)
    for wx, wy, I in wires:
        Bx, By = magnetic_field_wire(x, y, (wx, wy), I)
        Bx_total += Bx
        By_total += By
    return Bx_total, By_total

print("=== 磁场模拟 ===")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

configs = [
    {"wires": [(0, 0, 1e6)], "title": "单根直导线 (电流指向读者)", "range": 5},
    {"wires": [(-1, 0, 1e6), (1, 0, 1e6)], "title": "平行同向电流", "range": 5},
    {"wires": [(-1, 0, 1e6), (1, 0, -1e6)], "title": "平行反向电流", "range": 5},
]

for ax, cfg in zip(axes, configs):
    wires = cfg["wires"]
    r = cfg["range"]

    x = np.linspace(-r, r, 30)
    y = np.linspace(-r, r, 30)
    X, Y = np.meshgrid(x, y)

    Bx, By = total_B(X, Y, wires)
    B_mag = np.sqrt(Bx ** 2 + By ** 2)
    Bx_norm = Bx / (B_mag + 1e-15)
    By_norm = By / (B_mag + 1e-15)

    x_s = np.linspace(-r, r, 8)
    y_s = np.linspace(-r, r, 8)
    Xs, Ys = np.meshgrid(x_s, y_s)
    Bxs, Bys = total_B(Xs, Ys, wires)
    B_mags = np.sqrt(Bxs ** 2 + Bys ** 2)
    Bxs_n = Bxs / (B_mags + 1e-15)
    Bys_n = Bys / (B_mags + 1e-15)

    ax.streamplot(x, y, Bx_norm, By_norm, color=np.log1p(B_mag),
                  cmap="cool", density=1.5, linewidth=1, arrowsize=1)
    ax.quiver(Xs, Ys, Bxs_n, Bys_n, color="black", alpha=0.5, scale=20)

    for wx, wy, I in wires:
        color = "red" if I > 0 else "blue"
        marker = "⊙" if I > 0 else "⊗"
        ax.plot(wx, wy, "o", color=color, markersize=14, markeredgecolor="black", zorder=5)
        label = "I⊙" if I > 0 else "I⊗"
        ax.text(wx, wy, "+" if I > 0 else "×", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white", zorder=6)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(cfg["title"])
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.show()
