"""
ABCD ray tracing (geometric optics): a fan of parallel rays focused by a thin
lens. Each ray is the state (height x, angle theta); optical elements act as
2x2 matrices multiplied in sequence. All rays converge at the focal plane --
pure geometric optics (the lambda -> 0 limit), with no diffraction.
"""
import numpy as np
import matplotlib.pyplot as plt

f = 1.0           # focal length
d1 = 2.0          # propagation before lens
d2 = 2.0          # propagation after lens


def propagate(d):
    return np.array([[1.0, d], [0.0, 1.0]])


def thin_lens(f):
    return np.array([[1.0, 0.0], [-1.0 / f, 1.0]])


def M_at(z):
    """Total ABCD matrix from input plane to axial position z."""
    if z <= d1:
        return propagate(z)
    return propagate(z - d1) @ thin_lens(f) @ propagate(d1)


heights = np.linspace(-0.3, 0.3, 13)
zs = np.linspace(0, d1 + d2, 400)

fig, ax = plt.subplots(figsize=(9, 6))
for x0 in heights:
    xs = [(M_at(z) @ np.array([x0, 0.0]))[0] for z in zs]
    ax.plot(zs, xs, color="C0")

ax.axvline(d1, color="gray", ls="--", lw=1, label=f"lens (z = {d1})")
ax.axvline(d1 + f, color="red", ls=":", lw=1.5,
           label=f"focal plane (z = {d1 + f})")
ax.set_xlabel("axial position z")
ax.set_ylabel("ray height x")
ax.set_title("ABCD ray tracing: parallel rays focused by a thin lens")
ax.legend()
ax.grid(True, alpha=0.3)

plt.suptitle('abcd_ray_tracing')
plt.show()
print("09_abcd_ray_tracing.py done")
