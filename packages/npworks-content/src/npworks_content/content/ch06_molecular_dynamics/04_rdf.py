import numpy as np
import matplotlib.pyplot as plt


np.random.seed(7)
N = 64
L = 8.0
dt = 0.005
n_equil = 2000
n_sample = 3000
r_cut = L / 2.0
rho = N / (L * L)
T_target = 1.0

n_side = int(np.ceil(np.sqrt(N)))
spacing = L / n_side
pos = np.zeros((N, 2))
idx = 0
for ix in range(n_side):
    for iy in range(n_side):
        if idx < N:
            pos[idx, 0] = (ix + 0.5) * spacing
            pos[idx, 1] = (iy + 0.5) * spacing
            idx += 1
vel = np.random.normal(0, np.sqrt(T_target), (N, 2))
vel -= np.mean(vel, axis=0)
f_dof = 2 * N - 2
vel *= np.sqrt(T_target / (2.0 * 0.5 * np.sum(vel ** 2) / f_dof))


def compute_forces(pos):
    forces = np.zeros_like(pos)
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
    return forces


# 径向分布函数 g(r) 直方统计
dr_bin = 0.05
r_max = L / 2.0
bins = np.arange(0.0, r_max + dr_bin, dr_bin)
r_centers = 0.5 * (bins[:-1] + bins[1:])
shell_area = 2.0 * np.pi * r_centers * dr_bin
hist_acc = np.zeros(len(r_centers))

acc = compute_forces(pos)
n_used = 0
for step in range(n_equil + n_sample):
    pos = pos + vel * dt + 0.5 * acc * dt ** 2
    pos = pos - L * np.floor(pos / L)
    acc_new = compute_forces(pos)
    vel = vel + 0.5 * (acc + acc_new) * dt
    acc = acc_new
    if step >= n_equil and step % 20 == 0:
        # 统计所有 i<j 粒子对的距离（最小镜像）
        for i in range(N):
            rij = pos[i + 1:] - pos[i]
            rij = rij - L * np.round(rij / L)
            dist = np.sqrt(np.sum(rij ** 2, axis=1))
            h, _ = np.histogram(dist, bins=bins)
            hist_acc += h
        n_used += 1

# g(r) = 2 * hist / (N * rho * shell_area)
gr = 2.0 * hist_acc / (N * rho * shell_area * n_used)

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(r_centers, gr, 'b-', linewidth=1.5)
ax.axhline(1.0, color='gray', linestyle='--', linewidth=0.8, label='ideal gas (g=1)')
ax.axvline(2.0 ** (1.0 / 6.0), color='r', linestyle=':', linewidth=0.8,
           label=r"$r_{\min}=2^{1/6}\sigma$")
ax.set_xlabel('r / sigma')
ax.set_ylabel('g(r)')
ax.set_title('Radial Distribution Function g(r) of a 2D Lennard-Jones Liquid')
ax.set_xlim(0, r_max)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('rdf')

print("04_rdf.py done")

plt.show()
