"""
Deterministic fractals: Koch curve, Koch snowflake, Sierpinski triangle.
Generates the fractals by recursion and measures their box-counting
dimension, verifying the analytical values:
    Koch curve      D = log4/log3 ~ 1.262
    Sierpinski tri  D = log3/log2 ~ 1.585
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


def koch_segment(p1, p2, depth, segs):
    if depth == 0:
        segs.append((p1, p2))
        return
    a = p1 + (p2 - p1) / 3.0
    c = p1 + 2 * (p2 - p1) / 3.0
    # bump vertex b: rotate (c-a) by -60 deg about a
    v = c - a
    rot = np.array([0.5, -np.sqrt(3) / 2.0])  # (cos -60, sin -60) applied per coord
    b = a + np.array([v[0] * rot[0] - v[1] * rot[1],
                      v[0] * rot[1] + v[1] * rot[0]])
    koch_segment(p1, a, depth - 1, segs)
    koch_segment(a, b, depth - 1, segs)
    koch_segment(b, c, depth - 1, segs)
    koch_segment(c, p2, depth - 1, segs)


def build_koch_snowflake(depth):
    verts = [np.array([0.0, 0.0]),
             np.array([1.0, 0.0]),
             np.array([0.5, np.sqrt(3) / 2.0])]
    segs = []
    for i in range(3):
        koch_segment(verts[i], verts[(i + 1) % 3], depth, segs)
    return segs


def segments_to_points(segs, n_per_seg=8):
    pts = []
    for p1, p2 in segs:
        for t in np.linspace(0, 1, n_per_seg):
            pts.append(p1 + t * (p2 - p1))
    return np.array(pts)


def sierpinski_points(depth):
    """Sierpinski triangle as a point cloud via recursive subdivision."""
    tris = [(np.array([0.0, 0.0]),
             np.array([1.0, 0.0]),
             np.array([0.5, np.sqrt(3) / 2.0]))]
    for _ in range(depth):
        new = []
        for (a, b, c) in tris:
            ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
            new += [(a, ab, ca), (ab, b, bc), (ca, bc, c)]
        tris = new
    pts = []
    for (a, b, c) in tris:
        for s, t in np.random.rand(40, 2):
            if s + t > 1:
                s, t = 1 - s, 1 - t
            pts.append(a + s * (b - a) + t * (c - a))
    return np.array(pts)


def box_counting_dim(points, eps_factors=None):
    """Return (1/eps list, N(eps) list)."""
    xmin, ymin = points.min(axis=0)
    xmax, ymax = points.max(axis=0)
    L = max(xmax - xmin, ymax - ymin)
    if eps_factors is None:
        eps_factors = np.array([2 ** k for k in range(1, 9)])
    one_over_eps, Ns = [], []
    for k in eps_factors:
        eps = L / k
        bx = np.floor((points[:, 0] - xmin) / eps).astype(int)
        by = np.floor((points[:, 1] - ymin) / eps).astype(int)
        N = len(set(zip(bx.tolist(), by.tolist())))
        one_over_eps.append(1.0 / eps)
        Ns.append(N)
    return np.array(one_over_eps), np.array(Ns)


def fit_dim(one_over_eps, Ns, lo=2, hi=-2):
    """Linear fit of log N vs log(1/eps) over the scaling region."""
    x = np.log(one_over_eps[lo:hi])
    y = np.log(Ns[lo:hi])
    slope = np.polyfit(x, y, 1)[0]
    return slope


# ---- Build fractals ----
np.random.seed(0)
koch_segs = build_koch_snowflake(depth=5)
koch_pts = segments_to_points(koch_segs, n_per_seg=6)
sier_pts = sierpinski_points(depth=6)

# ---- Box-counting ----
oe_koch, N_koch = box_counting_dim(koch_pts)
oe_sier, N_sier = box_counting_dim(sier_pts)
D_koch = fit_dim(oe_koch, N_koch)
D_sier = fit_dim(oe_sier, N_sier)
D_koch_th = np.log(4) / np.log(3)
D_sier_th = np.log(3) / np.log(2)
print(f"Koch curve      D_meas={D_koch:.3f}  theory={D_koch_th:.3f}")
print(f"Sierpinski tri  D_meas={D_sier:.3f}  theory={D_sier_th:.3f}")

# ---- Plot ----
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
# snowflake
for p1, p2 in koch_segs:
    axes[0].plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', lw=0.5)
axes[0].set_aspect('equal'); axes[0].axis('off')
axes[0].set_title(f"Koch snowflake (D={D_koch:.3f})")
# sierpinski
axes[1].scatter(sier_pts[:, 0], sier_pts[:, 1], s=0.1, c='k')
axes[1].set_aspect('equal'); axes[1].axis('off')
axes[1].set_title(f"Sierpinski triangle (D={D_sier:.3f})")
# box-counting fits
axes[2].loglog(oe_koch, N_koch, 'o-', label=f"Koch (slope={D_koch:.3f})")
axes[2].loglog(oe_sier, N_sier, 's-', label=f"Sierpinski (slope={D_sier:.3f})")
axes[2].set_xlabel("1 / box size"); axes[2].set_ylabel("N(boxes)")
axes[2].set_title("Box-counting dimension")
axes[2].legend(); axes[2].grid(True, which='both', ls=':', alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch22_koch_sierpinski.png"), dpi=130)
print("saved ch22_koch_sierpinski.png")
