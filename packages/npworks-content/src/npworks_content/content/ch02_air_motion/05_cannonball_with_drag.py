import math
import matplotlib.pyplot as plt

g = 9.8
v0 = 700.0
dt = 0.1
k = 4.0e-5
angles = [30, 35, 40, 45, 50, 55]

plt.figure(figsize=(8, 6))

for angle in angles:
    x = 0.0
    y = 0.0
    angle_rad = angle * math.pi / 180.0
    vx = v0 * math.cos(angle_rad)
    vy = v0 * math.sin(angle_rad)
    xs = []
    ys = []
    while y >= 0:
        xs.append(x)
        ys.append(y)
        v = math.sqrt(vx * vx + vy * vy)
        x = x + vx * dt
        y = y + vy * dt
        vx = vx - k * v * vx * dt
        vy = vy - g * dt - k * v * vy * dt
    plt.plot(xs, ys, label='%d deg' % angle)

plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.title('Cannonball Trajectories (With Air Resistance)')
plt.legend()
plt.grid(True)
plt.suptitle('cannonball_with_drag')
plt.show()
