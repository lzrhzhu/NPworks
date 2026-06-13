import math
import matplotlib.pyplot as plt

g = 9.8
v0 = 700.0
dt = 0.1
k = 4.0e-5
angle = 38.0
angle_rad = angle * math.pi / 180.0

def derivatives(x, y, vx, vy):
    v = math.sqrt(vx * vx + vy * vy)
    return (vx, vy, -k * v * vx, -g - k * v * vy)

x_e, y_e = 0.0, 0.0
vx_e = v0 * math.cos(angle_rad)
vy_e = v0 * math.sin(angle_rad)
xe_list, ye_list = [x_e], [y_e]

while y_e >= 0:
    dx, dy, dvx, dvy = derivatives(x_e, y_e, vx_e, vy_e)
    x_e = x_e + dx * dt
    y_e = y_e + dy * dt
    vx_e = vx_e + dvx * dt
    vy_e = vy_e + dvy * dt
    if y_e >= 0:
        xe_list.append(x_e)
        ye_list.append(y_e)

x_r, y_r = 0.0, 0.0
vx_r = v0 * math.cos(angle_rad)
vy_r = v0 * math.sin(angle_rad)
xr_list, yr_list = [x_r], [y_r]

while y_r >= 0:
    k1 = derivatives(x_r, y_r, vx_r, vy_r)
    k2 = derivatives(x_r + 0.5 * dt * k1[0], y_r + 0.5 * dt * k1[1],
                     vx_r + 0.5 * dt * k1[2], vy_r + 0.5 * dt * k1[3])
    k3 = derivatives(x_r + 0.5 * dt * k2[0], y_r + 0.5 * dt * k2[1],
                     vx_r + 0.5 * dt * k2[2], vy_r + 0.5 * dt * k2[3])
    k4 = derivatives(x_r + dt * k3[0], y_r + dt * k3[1],
                     vx_r + dt * k3[2], vy_r + dt * k3[3])
    x_r = x_r + dt / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
    y_r = y_r + dt / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
    vx_r = vx_r + dt / 6.0 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
    vy_r = vy_r + dt / 6.0 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
    if y_r >= 0:
        xr_list.append(x_r)
        yr_list.append(y_r)

range_euler = xe_list[-1]
range_rk4 = xr_list[-1]

plt.figure(figsize=(10, 6))
plt.plot(xe_list, ye_list, 'r--', linewidth=1.5, label='Euler (range = {:.0f} m)'.format(range_euler))
plt.plot(xr_list, yr_list, 'b-', linewidth=1.5, label='RK4 (range = {:.0f} m)'.format(range_rk4))
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.title('Cannonball Trajectory: Euler vs RK4 (dt = {} s)'.format(dt))
plt.legend()
plt.grid(True, alpha=0.3)
plt.gca().set_aspect('equal')

plt.tight_layout()
plt.suptitle('rk4_cannonball')
plt.show()
print("09_rk4_cannonball.py done")
