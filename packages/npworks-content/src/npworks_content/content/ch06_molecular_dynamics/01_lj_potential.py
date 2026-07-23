import numpy as np
import matplotlib.pyplot as plt
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


IMG_DIR = _img_dir("ch06")

epsilon = 1.0
sigma = 1.0
r = np.linspace(0.9, 3.0, 500)
r_min_val = 2.0 ** (1.0 / 6.0) * sigma
V = 4.0 * epsilon * ((sigma / r) ** 12 - (sigma / r) ** 6)
F = 24.0 * epsilon * (2.0 * (sigma / r) ** 12 - (sigma / r) ** 6) / r

# --- 图1：Lennard-Jones 势能 V(r) ---
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(r, V, 'b-', linewidth=2)
ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
ax.axvline(x=r_min_val, color='r', linestyle=':', linewidth=0.8, label='r_min = 2^(1/6)*sigma')
ax.axvline(x=sigma, color='g', linestyle=':', linewidth=0.8, label='r = sigma (V=0)')
ax.set_xlabel('r / sigma')
ax.set_ylabel(r'$V(r)\,/\,\epsilon$')
ax.set_title('Lennard-Jones Potential')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(-1.5, 3.0)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch06_lj_potential.png"), dpi=130)
plt.close(fig)

# --- 图2：Lennard-Jones 力 F(r) ---
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(r, F, 'r-', linewidth=2)
ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
ax.axvline(x=r_min_val, color='r', linestyle=':', linewidth=0.8, label='r_min = 2^(1/6)*sigma')
ax.set_xlabel('r / sigma')
ax.set_ylabel(r'$F(r)\,\sigma\,/\,\epsilon$')
ax.set_title('Lennard-Jones Force')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(-3.0, 5.0)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch06_lj_force.png"), dpi=130)
plt.close(fig)

print("01_lj_potential.py done")
