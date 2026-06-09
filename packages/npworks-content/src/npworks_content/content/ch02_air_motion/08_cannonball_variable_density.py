import math
import matplotlib.pyplot as plt

k0 = 4.0e-5
dt = 0.1
v0 = 700.0
g = 9.8
T0 = 300.0
a = 6.5e-3
alpha = 2.5
angles = [35, 40, 45, 50, 55]

plt.figure(figsize=(8, 6))

for angle in angles:
    x = 0.0
    y = 0.0
    angle_rad = angle * math.pi / 180.0
    vx = v0 * math.cos(angle_rad)
    vy = v0 * math.sin(angle_rad)
    xs = [x]
    ys = [y]
    while y >= 0:
        density_factor = (1.0 - a * y / T0) ** alpha
        v = math.sqrt(vx * vx + vy * vy)
        x = x + vx * dt
        y = y + vy * dt
        vx = vx - k0 * density_factor * v * vx * dt
        vy = vy - g * dt - k0 * density_factor * v * vy * dt
        xs.append(x)
        ys.append(y)
    plt.plot(xs, ys, label='%d deg' % angle)

plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.title('Cannonball Trajectories (Variable Air Density)')
plt.legend()
plt.grid(True)
plt.suptitle('cannonball_variable_density')
plt.show()
