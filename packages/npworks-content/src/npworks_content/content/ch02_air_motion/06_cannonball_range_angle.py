import math
import matplotlib.pyplot as plt

g = 9.8
v0 = 700.0
dt = 0.1
k = 4.0e-5


def calculate_range(angle):
    x = 0.0
    y = 0.0
    angle_rad = angle * math.pi / 180.0
    vx = v0 * math.cos(angle_rad)
    vy = v0 * math.sin(angle_rad)
    prev_x = 0.0
    prev_y = 0.0
    while y >= 0:
        prev_y = y
        prev_x = x
        v = math.sqrt(vx * vx + vy * vy)
        x = x + vx * dt
        y = y + vy * dt
        vx = vx - k * v * vx * dt
        vy = vy - g * dt - k * v * vy * dt
    r = -prev_y / (y - prev_y)
    range_val = prev_x + r * (x - prev_x)
    return range_val


angle_data = []
range_data = []

for angle in range(0, 91, 1):
    current_range = calculate_range(float(angle))
    angle_data.append(angle)
    range_data.append(current_range)

plt.figure(figsize=(8, 6))
plt.plot(angle_data, range_data)
plt.xlabel('Launch Angle (deg)')
plt.ylabel('Range (m)')
plt.title('Range vs Launch Angle (With Air Resistance)')
plt.grid(True)
plt.suptitle('cannonball_range_angle')
plt.show()
