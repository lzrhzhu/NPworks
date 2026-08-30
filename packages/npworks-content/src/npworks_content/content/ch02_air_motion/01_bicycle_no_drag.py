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
plt.suptitle('bicycle_no_drag')
plt.show()
