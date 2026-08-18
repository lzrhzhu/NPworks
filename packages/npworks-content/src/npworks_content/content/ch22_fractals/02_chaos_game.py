"""
Iterated Function Systems via the chaos game.
Generates the Sierpinski triangle and the Barnsley fern by randomly
iterating affine contraction maps.
"""
import numpy as np
import matplotlib.pyplot as plt


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
fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(sier_pts[:, 0], sier_pts[:, 1], s=0.2, c='k')
ax.set_aspect('equal'); ax.axis('off')
ax.set_title("Chaos game: Sierpinski triangle")
plt.tight_layout(); plt.suptitle('chaos_game')
fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(fern_pts[:, 0], fern_pts[:, 1], s=0.15, c='green')
ax.set_aspect('equal'); ax.axis('off')
ax.set_title("Chaos game: Barnsley fern")
plt.tight_layout(); plt.suptitle('barnsley_fern')
print("saved ch22 chaos game + fern")

plt.show()
