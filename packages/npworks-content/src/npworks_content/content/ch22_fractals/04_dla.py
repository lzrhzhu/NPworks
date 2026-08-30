"""
Diffusion-Limited Aggregation (DLA): random walkers stick to a growing
cluster, producing a fractal with box-counting dimension ~1.71 in 2D.
"""
import numpy as np
import matplotlib.pyplot as plt


# grid; (i,j) with occupied flag. seed at center.
L = 200
occ = np.zeros((L, L), dtype=bool)
cx = cy = L // 2
occ[cx, cy] = True
r_max = 1.0                       # current cluster radius
r_launch = r_max + 5
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
        neighbours = ((i + 1 < L and occ[i + 1, j]) or
                      (i - 1 >= 0 and occ[i - 1, j]) or
                      (j + 1 < L and occ[i, j + 1]) or
                      (j - 1 >= 0 and occ[i, j - 1]))
        if neighbours:
            occ[i, j] = True
            n += 1
            rr = np.hypot(i - cx, j - cy)
            if rr > r_max:
                r_max = rr
                r_launch = r_max + 5
            break
        # acceleration: when far from the cluster (empty region), take a big
        # hop toward the centre instead of single-stepping through empty space.
        # This preserves the cluster statistics near the growth front while
        # eliminating the bulk of wasted random-walk steps.
        dist = np.hypot(i - cx, j - cy)
        if dist > r_max + 4:
            jump = int(dist - r_max - 2)
            if jump > 0:
                i -= int(round(jump * (i - cx) / dist))
                j -= int(round(jump * (j - cy) / dist))
                if not (0 <= i < L and 0 <= j < L):
                    break
                continue
        if dist > r_escape:
            break
        if safety > 8 * L:
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
    by = ((pts[:, 1] - ymin) / eps).astype(int)
    Ns.append(len(set(zip(bx.tolist(), by.tolist()))))
    inv_eps.append(1.0 / eps)
inv_eps = np.array(inv_eps); Ns = np.array(Ns)
# fit middle scaling region
m = (inv_eps > 1.0 / (Lx / 6)) & (inv_eps < 1.0 / 8)
slope = np.polyfit(np.log(inv_eps[m]), np.log(Ns[m]), 1)[0]
print(f"DLA box-counting dim ~ {slope:.3f}")

# --- plot ---
fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(occ, cmap='Greens', origin='lower')
ax.set_title(f"DLA cluster ({N_target} particles)")
ax.set_xlabel("x (格点)"); ax.set_ylabel("y (格点)")
plt.tight_layout(); plt.suptitle('dla')
fig, ax = plt.subplots(figsize=(7, 5.5))
ax.loglog(inv_eps, Ns, 'o-')
ax.set_xlabel("1 / box size"); ax.set_ylabel("N(boxes)")
ax.set_title(f"Box-counting: D ~ {slope:.3f}")
plt.tight_layout(); plt.suptitle('dla_boxcount')
print("saved ch22 dla + boxcount")

plt.show()
