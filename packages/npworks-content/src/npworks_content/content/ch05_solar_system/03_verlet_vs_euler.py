import numpy as np
import matplotlib.pyplot as plt

GM = 4.0 * np.pi ** 2

dt = 0.005
T = 5.0
N = int(T / dt)

def simulate_euler(dt, N):
    x, y = 1.0, 0.0
    vx, vy = 0.0, 2.0 * np.pi
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
    vx, vy = 0.0, 2.0 * np.pi
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
    vx, vy = 0.0, 2.0 * np.pi
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

fig, axes = plt.subplots(2, 1, figsize=(10, 8))

axes[0].plot(ts, E_euler, 'r-', linewidth=0.8, label='Euler')
axes[0].plot(ts, E_verlet, 'b-', linewidth=0.8, label='Velocity Verlet')
axes[0].plot(ts, E_cromer, 'g-', linewidth=0.8, label='Euler-Cromer')
axes[0].set_xlabel('Time (year)')
axes[0].set_ylabel('Total Energy')
axes[0].set_title('Total Energy: Verlet vs Euler vs Euler-Cromer')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

dE_euler = (E_euler - E0) / abs(E0)
dE_verlet = (E_verlet - E0) / abs(E0)
dE_cromer = (E_cromer - E0) / abs(E0)

axes[1].plot(ts, dE_euler, 'r-', linewidth=0.8, label='Euler')
axes[1].plot(ts, dE_verlet, 'b-', linewidth=0.8, label='Velocity Verlet')
axes[1].plot(ts, dE_cromer, 'g-', linewidth=0.8, label='Euler-Cromer')
axes[1].set_xlabel('Time (year)')
axes[1].set_ylabel('Relative Energy Drift dE/|E0|')
axes[1].set_title('Energy Conservation Comparison')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()

plt.suptitle('verlet_vs_euler')
plt.show()
print('ch05_verlet_vs_euler.png saved')
