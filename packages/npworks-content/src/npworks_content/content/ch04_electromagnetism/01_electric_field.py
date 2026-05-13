# -*- coding: utf-8 -*-
# 4.1 电场线
# 点电荷电场可视化

import numpy as np
import matplotlib.pyplot as plt

k = 8.99e9

def electric_field(x, y, charges):
    Ex = np.zeros_like(x, dtype=float)
    Ey = np.zeros_like(y, dtype=float)
    for qx, qy, q in charges:
        dx = x - qx
        dy = y - qy
        r = np.sqrt(dx ** 2 + dy ** 2)
        r = np.maximum(r, 0.1)
        E = k * q / r ** 2
        Ex += E * dx / r
        Ey += E * dy / r
    return Ex, Ey

def electric_potential(x, y, charges):
    V = np.zeros_like(x, dtype=float)
    for qx, qy, q in charges:
        dx = x - qx
        dy = y - qy
        r = np.sqrt(dx ** 2 + dy ** 2)
        r = np.maximum(r, 0.1)
        V += k * q / r
    return V

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

configs = [
    {"charges": [(0, 0, 1)], "title": "正点电荷"},
    {"charges": [(0, 0, -1)], "title": "负点电荷"},
    {"charges": [(-1, 0, 1), (1, 0, -1)], "title": "电偶极子"},
]

for ax, cfg in zip(axes, configs):
    charges = cfg["charges"]

    x = np.linspace(-4, 4, 30)
    y = np.linspace(-4, 4, 30)
    X, Y = np.meshgrid(x, y)

    Ex, Ey = electric_field(X, Y, charges)
    E_mag = np.sqrt(Ex ** 2 + Ey ** 2)
    Ex_norm = Ex / (E_mag + 1e-10)
    Ey_norm = Ey / (E_mag + 1e-10)

    x_fine = np.linspace(-4, 4, 200)
    y_fine = np.linspace(-4, 4, 200)
    Xf, Yf = np.meshgrid(x_fine, y_fine)
    V = electric_potential(Xf, Yf, charges)
    V = np.clip(V, -1e11, 1e11)

    levels = np.linspace(np.percentile(V, 5), np.percentile(V, 95), 20)
    ax.contourf(Xf, Yf, V, levels=levels, cmap="RdBu_r", alpha=0.3)
    ax.quiver(X, Y, Ex_norm, Ey_norm, E_mag, cmap="hot", alpha=0.7, scale=25)

    for qx, qy, q in charges:
        color = "red" if q > 0 else "blue"
        sign = "+" if q > 0 else "-"
        ax.plot(qx, qy, "o", color=color, markersize=12, markeredgecolor="black")
        ax.text(qx, qy, sign, ha="center", va="center", fontsize=10, fontweight="bold", color="white")

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(cfg["title"])
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.show()
