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


IMG_DIR = _img_dir("ch01")
os.makedirs(IMG_DIR, exist_ok=True)

t = np.linspace(0, 10 * np.pi, 500)
x = np.cos(t)
y = np.sin(t)
z = t / 4.0

fig = plt.figure(figsize=(8, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot(x, y, z, 'b-', linewidth=1.2)
ax.set_title('3D Helix')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch01_plot_3d.png"), dpi=130)
plt.close(fig)

print("02_plot_3d.py done")
