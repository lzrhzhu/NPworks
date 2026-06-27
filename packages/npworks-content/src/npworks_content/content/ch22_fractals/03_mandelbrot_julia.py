"""
Escape-time fractals: Mandelbrot set and a few Julia sets for z -> z^2 + c.
Uses smooth (continuous) escape-time coloring.
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


def escape_time(c_plane, z0, n_max=200, bailout=1e6):
    """z0: initial array (same shape as c_plane). Returns smooth iteration count."""
    z = z0.copy()
    count = np.zeros(z.shape, dtype=float)
    escaped = np.zeros(z.shape, dtype=bool)
    for n in range(1, n_max + 1):
        z = z * z + c_plane
        newly = (np.abs(z) > 2) & (~escaped)
        count[newly] = n - np.log(np.log(np.abs(z[newly])) / np.log(2)) / np.log(2)
        escaped |= newly
        if escaped.all():
            break
    count[~escaped] = n_max  # treat as inside the set
    return count


# --- Mandelbrot: c-plane, z0 = 0 ---
N = 700
x = np.linspace(-2.2, 0.8, N)
y = np.linspace(-1.2, 1.2, N)
X, Y = np.meshgrid(x, y)
C = X + 1j * Y
mandel = escape_time(C, np.zeros_like(C))

# --- Julia sets: fixed c, z0-plane ---
c_values = [-0.7269 + 0.1889j,   # dendrite-like (inside M boundary)
            -0.8 + 0.156j,       # connected
            0.285 + 0.01j]       # near-boundary spiral
julias = []
xj = np.linspace(-1.6, 1.6, N)
yj = np.linspace(-1.2, 1.2, N)
Xj, Yj = np.meshgrid(xj, yj)
Z0 = Xj + 1j * Yj
for c in c_values:
    julias.append(escape_time(np.full_like(Z0, c), Z0, n_max=150))

# --- plot ---
fig, axes = plt.subplots(2, 2, figsize=(11, 10))
axes[0, 0].imshow(mandel, extent=[x[0], x[-1], y[0], y[-1]],
                  cmap='magma', origin='lower', aspect='equal')
axes[0, 0].set_title("Mandelbrot set")
for ax, c, im in zip([axes[0, 1], axes[1, 0], axes[1, 1]], c_values, julias):
    ax.imshow(im, extent=[xj[0], xj[-1], yj[0], yj[-1]],
              cmap='magma', origin='lower', aspect='equal')
    ax.set_title(f"Julia set  c = {c:.4f}")
for ax in axes.flat:
    ax.set_xlabel("Re"); ax.set_ylabel("Im")
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch22_mandelbrot_julia.png"), dpi=130)
print("saved ch22_mandelbrot_julia.png")
