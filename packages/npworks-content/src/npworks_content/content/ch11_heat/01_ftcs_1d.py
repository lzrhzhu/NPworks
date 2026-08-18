import numpy as np
import matplotlib.pyplot as plt


L = 1.0
Nx = 50
alpha = 0.01
t_end = 10.0
dx = L / Nx
r = 0.4
dt = r * dx ** 2 / alpha
Nt = int(t_end / dt)

x = np.linspace(0, L, Nx + 1)
T_left, T_right = 100.0, 0.0
T_ss = T_left + (T_right - T_left) * x / L

T = np.zeros(Nx + 1)
T[0] = T_left
T[-1] = T_right
snapshot_times = [0, 0.5, 1.0, 2.0, 5.0, 10.0]
snapshots = {0: T.copy()}
time_elapsed = 0.0
spacetime = []
st_times = []

for n in range(Nt):
    T_new = T.copy()
    T_new[1:-1] = T[1:-1] + r * (T[2:] - 2 * T[1:-1] + T[:-2])
    T_new[0] = T_left
    T_new[-1] = T_right
    T = T_new
    time_elapsed += dt
    for st in snapshot_times:
        if abs(time_elapsed - st) < dt / 2 and st not in snapshots:
            snapshots[st] = T.copy()
    if n % max(1, Nt // 100) == 0:
        spacetime.append(T.copy())
        st_times.append(time_elapsed)

colors = plt.cm.viridis(np.linspace(0, 1, len(snapshot_times)))

# --- 图1：温度快照 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
for idx, t_label in enumerate(sorted(snapshots.keys())):
    ax.plot(x, snapshots[t_label], color=colors[idx], label=f'$t = {t_label:.1f}$ s')
ax.plot(x, T_ss, 'k--', linewidth=2, label='Steady state')
ax.set_xlabel('Position $x$ (m)')
ax.set_ylabel('Temperature $T$')
ax.set_title(f'FTCS: Temperature Snapshots ($r = {r}$)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('ftcs_1d')

# --- 图2：时空图 ---
spacetime = np.array(spacetime)
st_times = np.array(st_times)
X, Tt = np.meshgrid(x, st_times)
fig, ax = plt.subplots(figsize=(8, 5.5))
pcm = ax.pcolormesh(X, Tt, spacetime, cmap='hot', shading='auto')
plt.colorbar(pcm, ax=ax, label='Temperature $T$')
ax.set_xlabel('Position $x$ (m)')
ax.set_ylabel('Time $t$ (s)')
ax.set_title('FTCS: Space-Time Temperature Diagram')
plt.tight_layout()
plt.suptitle('ftcs_1d_spacetime')

print(f"01_ftcs_1d.py done (r={r}, dt={dt:.6f}, Nt={Nt})")

plt.show()
