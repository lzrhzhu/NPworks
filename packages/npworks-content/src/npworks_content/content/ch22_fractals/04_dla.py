"""
Diffusion-Limited Aggregation (DLA): random walkers stick to a growing
cluster, producing a fractal with box-counting dimension ~1.71 in 2D.
"""
import numpy as np
import matplotlib.pyplot as plt
import os


def _img_dir(ch):
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(d, "markdown")):
            return os.path.join(d, "markdown", "images", ch)
        d = os.path.dirname(d)
    # 未找到教材 markdown/images（PyPI 安装或独立运行）：回退到用户可写目录
    out = os.path.join(os.path.expanduser("~"), "npworks_figures", ch)
    os.makedirs(out, exist_ok=True)
    return out


IMG_DIR = _img_dir("ch22")

# grid; (i,j) with occupied flag. seed at center.
L = 200
occ = np.zeros((L, L), dtype=bool)
cx = cy = L // 2
occ[cx, cy] = True
r_max = 1.0                       # current cluster radius
r_launch = r_max + 8
r_escape = (L // 2) - 3

steps4 = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]])
N_target = 2500
n = 0
rng = np.random.default_rng(0)
while n < N_target:
    # launch on a circle of radius r_launch
    ang = rng.uniform(0, 2 * np.pi)
    r = r_launch
    i = int(cx + r * np.cos(ang))
    j = int(cy + r * np.sin(ang))
    if not (0 <= i < L and 0 <= j < L):
        continue
    safety = 0
    while True:
        d = rng.integers(0, 4)
        i += steps4[d, 0]
        j += steps4[d, 1]
        safety += 1
        if not (0 <= i < L and 0 <= j < L):
            break
        # check neighbours for sticking
        if (occ[(i + 1) % L, j] or occ[(i - 1) % L, j] or
                occ[i, (j + 1) % L] or occ[i, (j - 1) % L]):
            occ[i, j] = True
            n += 1
            rr = np.hypot(i - cx, j - cy)
            if rr > r_max:
                r_max = rr
                r_launch = r_max + 10
            break
        if np.hypot(i - cx, j - cy) > r_escape:
            break
        if safety > 20 * L:
            break
    if n % 1000 == 0 and n > 0:
        print(f"  DLA particles: {n}, r_max={r_max:.0f}")

# --- box-counting dimension ---
ys, xs = np.where(occ)
pts = np.column_stack([xs, ys]).astype(float)
xmin, xmax = pts[:, 0].min(), pts[:, 0].max()
ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
Lx = xmax - xmin
Ly = ymax - ymin
ks = np.unique(np.logspace(np.log10(4), np.log10(Lx / 3), 18).astype(int))
inv_eps, Ns = [], []
for k in ks:
    eps = Lx / k
    bx = ((pts[:, 0] - xmin) / eps).astype(int)
    by = ((pts[:, 1] - ymin) / (Ly / k)).astype(int)
    Ns.append(len(set(zip(bx.tolist(), by.tolist()))))
    inv_eps.append(1.0 / eps)
inv_eps = np.array(inv_eps); Ns = np.array(Ns)
# fit middle scaling region
m = (inv_eps > 1.0 / (Lx / 6)) & (inv_eps < 1.0 / 8)
slope = np.polyfit(np.log(inv_eps[m]), np.log(Ns[m]), 1)[0]
print(f"DLA box-counting dim ~ {slope:.3f}")

# --- plot ---
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
axes[0].imshow(occ, cmap='Greens', origin='lower')
axes[0].set_title(f"DLA cluster ({N_target} particles)")
axes[0].axis('off')
axes[1].loglog(inv_eps, Ns, 'o-')
axes[1].set_xlabel("1 / box size"); axes[1].set_ylabel("N(boxes)")
axes[1].set_title(f"Box-counting: D ~ {slope:.3f}")
axes[1].grid(True, which='both', ls=':', alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch22_dla.png"), dpi=130)
print("saved ch22_dla.png")
