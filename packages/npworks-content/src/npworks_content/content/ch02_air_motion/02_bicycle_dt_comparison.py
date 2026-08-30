import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'lines.markersize': 5,
    'axes.grid': False, 'axes.unicode_minus': False,
})

P = 400
m = 70
t_start = 0.0
t_end = 10.0
v_0 = 4

line_styles = ['-', '--', '-.']
for N, line_style in zip([100, 10, 2], line_styles):
    dt = (t_end - t_start) / N
    v = np.zeros(N + 1)
    t = np.zeros(N + 1)
    v[0] = v_0
    t[0] = t_start
    for i in range(N):
        v[i + 1] = v[i] + (P * dt) / (m * v[i])
        t[i + 1] = t[i] + dt
    plt.plot(t, v, linestyle=line_style,
             label='Numerical, N=%d, dt=%.2f' % (N, dt))

N_exact = 1000
t_exact = np.linspace(t_start, t_end, N_exact + 1)
v_exact = np.sqrt(2 * P / m * t_exact + v_0**2)
plt.plot(t_exact, v_exact, color='black', linestyle=':', linewidth=2.0,
         label='Analytical Solution')

plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.legend(frameon=False)
plt.xlim(t_start, t_end)
plt.ylim(bottom=0)
plt.suptitle('bicycle_dt_comparison')
plt.show()
