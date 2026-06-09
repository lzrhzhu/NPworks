import numpy as np
import matplotlib.pyplot as plt

P = 400
m = 70
t_start = 0.0
t_end = 10.0
v_0 = 4

for N in [100, 10, 2]:
    dt = (t_end - t_start) / N
    v = np.zeros(N + 1)
    t = np.zeros(N + 1)
    v[0] = v_0
    t[0] = t_start
    for i in range(N):
        v[i + 1] = v[i] + (P * dt) / (m * v[i])
        t[i + 1] = t[i] + dt
    plt.plot(t, v, label='Numerical, N=%d, dt=%.2f' % (N, dt))

N_exact = 1000
t_exact = np.linspace(t_start, t_end, N_exact + 1)
v_exact = np.sqrt(2 * P / m * t_exact + v_0**2)
plt.plot(t_exact, v_exact, 'r--', label='Analytical Solution')

plt.title('Numerical vs Analytical Solution')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.legend()
plt.grid(True)
plt.xlim(t_start, t_end)
plt.ylim(bottom=0)
plt.suptitle('bicycle_dt_comparison')
plt.show()
