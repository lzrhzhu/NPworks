import math
import matplotlib.pyplot as plt

g = 9.8
v0 = 600.0
dt = 0.1
k = 4.0e-5
target_distance = 15000.0
tolerance = 0.001


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


prev_land = calculate_range(15.0)
low_angle = 15.0
high_angle = 15.0

for angle_int in range(16, 46):
    current_land = calculate_range(float(angle_int))
    if (current_land - target_distance) * (prev_land - target_distance) < 0:
        low_angle = float(angle_int - 1)
        high_angle = float(angle_int)
        break
    else:
        prev_land = current_land

low_land = calculate_range(low_angle)

while (high_angle - low_angle) > tolerance:
    mid_angle = (low_angle + high_angle) / 2.0
    mid_land = calculate_range(mid_angle)
    if (mid_land - target_distance) * (low_land - target_distance) < 0:
        high_angle = mid_angle
    else:
        low_angle = mid_angle
        low_land = mid_land

best_angle = (low_angle + high_angle) / 2.0
print('Best angle: %.3f deg' % best_angle)
print('Range at best angle: %.1f m' % calculate_range(best_angle))

x = 0.0
y = 0.0
angle_rad = best_angle * math.pi / 180.0
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

plt.figure(figsize=(8, 6))
plt.plot(xs, ys, label='%.2f deg' % best_angle)
plt.axvline(x=target_distance, color='r', linestyle='--', label='Target 15 km')
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.title('Bisection: Cannonball Trajectory Hitting 15 km Target')
plt.legend()
plt.grid(True)
plt.suptitle('cannonball_bisection')
plt.show()
