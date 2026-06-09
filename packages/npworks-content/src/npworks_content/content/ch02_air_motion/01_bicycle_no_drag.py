import matplotlib.pyplot as plt

P = 400
dt = 0.1
N = 1001
m = 70
v_0 = 4

t = [0] * N
v = [v_0] * N

for i in range(N - 1):
    if v[i] != 0:
        v[i + 1] = v[i] + P * dt / (m * v[i])
        t[i + 1] = t[i] + dt

plt.plot(t, v)
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.title('Velocity-Time Curve (No Air Resistance)')
plt.grid(True)
plt.suptitle('bicycle_no_drag')
plt.show()
