import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

N_particles = 36
L = 8.0
dt = 0.005
n_equil = 2000
n_sample = 5000
n_total = n_equil + n_sample
r_cut = L / 2.0
T_target = 0.8

n_side = int(np.ceil(np.sqrt(N_particles)))
spacing = L / n_side
pos = np.zeros((N_particles, 2))
idx = 0
for ix in range(n_side):
    for iy in range(n_side):
        if idx < N_particles:
            pos[idx, 0] = (ix + 0.5) * spacing
            pos[idx, 1] = (iy + 0.5) * spacing
            idx += 1

vel = np.random.normal(0, np.sqrt(T_target), (N_particles, 2))
vel -= np.mean(vel, axis=0)
f_dof = 2 * N_particles - 2
KE0 = 0.5 * np.sum(vel ** 2)
T_act = 2.0 * KE0 / f_dof
vel *= np.sqrt(T_target / T_act)

pos_unwrapped = pos.copy()
pos_prev = pos.copy()

def compute_forces(pos, L, r_cut):
    N = pos.shape[0]
    forces = np.zeros_like(pos)
    PE = 0.0
    V_cut = 4.0 * ((1.0 / r_cut) ** 12 - (1.0 / r_cut) ** 6)
    for i in range(N):
        for j in range(i + 1, N):
            rij = pos[i] - pos[j]
            rij = rij - L * np.round(rij / L)
            r2 = np.dot(rij, rij)
            if r2 < r_cut ** 2:
                inv_r2 = 1.0 / r2
                inv_r6 = inv_r2 ** 3
                inv_r12 = inv_r6 ** 2
                fmag = 24.0 * (2.0 * inv_r12 - inv_r6) * inv_r2
                fij = fmag * rij
                forces[i] += fij
                forces[j] -= fij
                PE += 4.0 * (inv_r12 - inv_r6) - V_cut
    return forces, PE

acc, _ = compute_forces(pos, L, r_cut)

origin = pos_unwrapped.copy()
n_save = n_sample
msd_data = []

for step in range(n_total):
    pos_prev = pos.copy()
    pos = pos + vel * dt + 0.5 * acc * dt ** 2
    delta = pos - pos_prev
    delta = delta - L * np.round(delta / L)
    pos_unwrapped = pos_unwrapped + delta
    pos = pos - L * np.floor(pos / L)
    acc_new, PE = compute_forces(pos, L, r_cut)
    vel = vel + 0.5 * (acc + acc_new) * dt
    acc = acc_new

    if step >= n_equil:
        disp = pos_unwrapped - origin
        msd = np.mean(np.sum(disp ** 2, axis=1))
        msd_data.append(msd)

msd_data = np.array(msd_data)
times = np.arange(len(msd_data)) * dt

slope, intercept = np.polyfit(times, msd_data, 1)
D = slope / (2.0 * 2.0)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].plot(times, msd_data, 'b-', linewidth=1, label='MSD from MD')
axes[0].plot(times, slope * times + intercept, 'r--', linewidth=2, label='Linear fit: slope={:.4f}'.format(slope))
axes[0].set_xlabel('Time')
axes[0].set_ylabel('MSD')
axes[0].set_title('Mean Square Displacement from MD')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].loglog(times, msd_data, 'b-', linewidth=1, label='MSD')
axes[1].loglog(times, slope * times, 'r--', linewidth=1.5, label='Slope=1 (diffusive)')
axes[1].set_xlabel('Time (log)')
axes[1].set_ylabel('MSD (log)')
axes[1].set_title('MSD (log-log)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()

plt.suptitle('msd')
plt.show()
print('ch05_msd.png saved')
print('D (2D) = {:.6f}'.format(D))
