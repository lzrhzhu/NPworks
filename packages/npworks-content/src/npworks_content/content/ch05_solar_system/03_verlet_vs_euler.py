import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300,
    'figure.figsize': (6.4, 4.0),
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'axes.grid': False,
    'axes.unicode_minus': False,
})

GM = 1.0

dt = 0.01 * np.pi           # dimensionless step Δτ; 0.005 year
T = 10.0 * np.pi            # dimensionless end time τ; 5 years
N = int(T / dt)

def simulate_euler(dt, N):
    x, y = 1.0, 0.0
    vx, vy = 0.0, 1.0
    E = np.zeros(N + 1)
    r = np.sqrt(x**2 + y**2)
    E[0] = 0.5 * (vx**2 + vy**2) - GM / r
    for i in range(N):
        r = np.sqrt(x**2 + y**2)
        ax = -GM * x / r**3
        ay = -GM * y / r**3
        x = x + vx * dt
        y = y + vy * dt
        vx = vx + ax * dt
        vy = vy + ay * dt
        r = np.sqrt(x**2 + y**2)
        E[i + 1] = 0.5 * (vx**2 + vy**2) - GM / r
    return E

def simulate_verlet(dt, N):
    x, y = 1.0, 0.0
    vx, vy = 0.0, 1.0
    E = np.zeros(N + 1)
    r = np.sqrt(x**2 + y**2)
    ax = -GM * x / r**3
    ay = -GM * y / r**3
    E[0] = 0.5 * (vx**2 + vy**2) - GM / r
    for i in range(N):
        x = x + vx * dt + 0.5 * ax * dt**2
        y = y + vy * dt + 0.5 * ay * dt**2
        r = np.sqrt(x**2 + y**2)
        ax_new = -GM * x / r**3
        ay_new = -GM * y / r**3
        vx = vx + 0.5 * (ax + ax_new) * dt
        vy = vy + 0.5 * (ay + ay_new) * dt
        ax = ax_new
        ay = ay_new
        E[i + 1] = 0.5 * (vx**2 + vy**2) - GM / r
    return E

def simulate_euler_cromer(dt, N):
    x, y = 1.0, 0.0
    vx, vy = 0.0, 1.0
    E = np.zeros(N + 1)
    r = np.sqrt(x**2 + y**2)
    E[0] = 0.5 * (vx**2 + vy**2) - GM / r
    for i in range(N):
        r = np.sqrt(x**2 + y**2)
        ax = -GM * x / r**3
        ay = -GM * y / r**3
        vx = vx + ax * dt
        vy = vy + ay * dt
        x = x + vx * dt
        y = y + vy * dt
        r = np.sqrt(x**2 + y**2)
        E[i + 1] = 0.5 * (vx**2 + vy**2) - GM / r
    return E

E_euler = simulate_euler(dt, N)
E_verlet = simulate_verlet(dt, N)
E_cromer = simulate_euler_cromer(dt, N)
ts = np.arange(N + 1) * dt

E0 = E_verlet[0]

fig, ax = plt.subplots()
ax.plot(ts, E_euler, color='#D55E00', linestyle='-', label='Euler')
ax.plot(ts, E_verlet, color='#0072B2', linestyle='--', label='Velocity Verlet')
ax.plot(ts, E_cromer, color='#009E73', linestyle='-.', label='Euler-Cromer')
ax.set_xlabel(r'$\tau$ ( $T_0$ )'); ax.set_ylabel('Dimensionless total energy')
ax.set_title('Energy Comparison'); ax.legend(frameon=False)
plt.tight_layout(); plt.suptitle('verlet_vs_euler')
dE_euler = (E_euler - E0) / abs(E0)
dE_verlet = (E_verlet - E0) / abs(E0)
dE_cromer = (E_cromer - E0) / abs(E0)
fig, ax = plt.subplots()
ax.plot(ts, dE_euler, color='#D55E00', linestyle='-', label='Euler')
ax.plot(ts, dE_verlet, color='#0072B2', linestyle='--', label='Velocity Verlet')
ax.plot(ts, dE_cromer, color='#009E73', linestyle='-.', label='Euler-Cromer')
ax.set_xlabel(r'$\tau$ ( $T_0$ )'); ax.set_ylabel(r'Relative energy drift $\Delta E/|E_0|$')
ax.set_title('Energy Drift Comparison'); ax.legend(frameon=False)
plt.tight_layout(); plt.suptitle('verlet_vs_euler_drift')
print('ch05_verlet_vs_euler done')

plt.show()
