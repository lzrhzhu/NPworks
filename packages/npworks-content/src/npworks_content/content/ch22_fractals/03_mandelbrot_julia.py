"""
Escape-time fractals: Mandelbrot set and a few Julia sets for z -> z^2 + c.
Uses smooth (continuous) escape-time coloring.
"""
import numpy as np
import matplotlib.pyplot as plt


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
fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(mandel, extent=[x[0], x[-1], y[0], y[-1]], cmap='magma', origin='lower', aspect='equal')
ax.set_title("Mandelbrot set"); ax.set_xlabel("Re"); ax.set_ylabel("Im")
plt.tight_layout(); plt.suptitle('mandelbrot')
for c, im in zip(c_values, julias):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(im, extent=[xj[0], xj[-1], yj[0], yj[-1]], cmap='magma', origin='lower', aspect='equal')
    ax.set_title(f"Julia set  c = {c:.4f}"); ax.set_xlabel("Re"); ax.set_ylabel("Im")
    plt.tight_layout(); plt.suptitle(f'julia_{c:.4f}')
print("saved ch22 mandelbrot + julias")

plt.show()
