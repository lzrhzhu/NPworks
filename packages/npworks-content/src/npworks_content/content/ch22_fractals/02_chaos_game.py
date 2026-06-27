"""
Iterated Function Systems via the chaos game.
Generates the Sierpinski triangle and the Barnsley fern by randomly
iterating affine contraction maps.
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
np.random.seed(1)


def chaos_game(maps, probs, n_iter, burn_in=100):
    """maps: list of functions x->x'; probs: corresponding probabilities."""
    p = np.array([0.0, 0.0])
    pts = []
    for i in range(n_iter):
        r = np.random.rand()
        cum = 0.0
        for f, pr in zip(maps, probs):
            cum += pr
            if r <= cum:
                p = f(p)
                break
        if i >= burn_in:
            pts.append(p.copy())
    return np.array(pts)


# --- Sierpinski triangle: 3 maps, each moves halfway to a vertex ---
verts = [np.array([0.0, 0.0]), np.array([1.0, 0.0]),
         np.array([0.5, np.sqrt(3) / 2.0])]
sier_maps = [lambda p, v=v: 0.5 * (p + v) for v in verts]
sier_pts = chaos_game(sier_maps, [1 / 3, 1 / 3, 1 / 3], 60000)

# --- Barnsley fern: 4 affine maps ---
fern_maps = [
    lambda p: np.array([0.0, 0.16 * p[1]]),
    lambda p: np.array([0.85 * p[0] + 0.04 * p[1],
                        -0.04 * p[0] + 0.85 * p[1] + 1.6]),
    lambda p: np.array([0.20 * p[0] - 0.26 * p[1],
                        0.23 * p[0] + 0.22 * p[1] + 1.6]),
    lambda p: np.array([-0.15 * p[0] + 0.28 * p[1],
                        0.26 * p[0] + 0.24 * p[1] + 0.44]),
]
fern_pts = chaos_game(fern_maps, [0.01, 0.85, 0.07, 0.07], 80000)

# --- plot ---
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
axes[0].scatter(sier_pts[:, 0], sier_pts[:, 1], s=0.2, c='k')
axes[0].set_aspect('equal'); axes[0].axis('off')
axes[0].set_title("Chaos game: Sierpinski triangle")
axes[1].scatter(fern_pts[:, 0], fern_pts[:, 1], s=0.15, c='green')
axes[1].set_aspect('equal'); axes[1].axis('off')
axes[1].set_title("Chaos game: Barnsley fern")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch22_chaos_game.png"), dpi=130)
print("saved ch22_chaos_game.png")
