import numpy as np
import matplotlib.pyplot as plt


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
plt.suptitle('plot_3d')

print("02_plot_3d.py done")

plt.show()
