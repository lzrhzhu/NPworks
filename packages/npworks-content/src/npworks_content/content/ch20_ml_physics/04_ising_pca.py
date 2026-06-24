import numpy as np
import matplotlib.pyplot as plt


def ising_2d_mc(L, T, N_therm, N_measure, seed=42):
    rng = np.random.default_rng(seed)
    N = L * L
    beta = 1.0 / T
    s = np.ones((L, L), dtype=np.int8)
    exp_table = {dE: np.exp(-beta * dE) for dE in [-8, -4, 0, 4, 8]}

    for _ in range(N_therm):
        for _ in range(N):
            i, j = int(rng.integers(L)), int(rng.integers(L))
            nb = (int(s[(i-1) % L, j]) + int(s[(i+1) % L, j]) +
                  int(s[i, (j-1) % L]) + int(s[i, (j+1) % L]))
            dE = 2 * int(s[i, j]) * nb
            if dE <= 0 or rng.random() < exp_table[dE]:
                s[i, j] = np.int8(-s[i, j])

    for _ in range(N_measure):
        for _ in range(N):
            i, j = int(rng.integers(L)), int(rng.integers(L))
            nb = (int(s[(i-1) % L, j]) + int(s[(i+1) % L, j]) +
                  int(s[i, (j-1) % L]) + int(s[i, (j+1) % L]))
            dE = 2 * int(s[i, j]) * nb
            if dE <= 0 or rng.random() < exp_table[dE]:
                s[i, j] = np.int8(-s[i, j])

    return s.copy()


L = 16
T_range = np.linspace(1.5, 3.5, 15)
n_samples_per_T = 15

print("Generating Ising configurations...")
all_configs = []
all_temps = []

for tidx, T in enumerate(T_range):
    for s_idx in range(n_samples_per_T):
        config = ising_2d_mc(L, T, N_therm=500, N_measure=300,
                             seed=42 + tidx * 100 + s_idx)
        all_configs.append(config.flatten().astype(float))
        all_temps.append(T)
    print(f"  T={T:.2f} done ({(tidx+1)}/{len(T_range)})")

X = np.array(all_configs)
T_data = np.array(all_temps)

X_mean = np.mean(X, axis=0)
X_centered = X - X_mean

cov_matrix = X_centered.T @ X_centered / len(X)

eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

X_pca = X_centered @ eigenvectors[:, :2]

var_explained = eigenvalues[:2] / np.sum(eigenvalues)
print(f"Variance explained: PC1={var_explained[0]:.4f}, PC2={var_explained[1]:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

scatter = axes[0].scatter(X_pca[:, 0], X_pca[:, 1], c=T_data,
                          cmap='coolwarm', s=15, alpha=0.7)
plt.colorbar(scatter, ax=axes[0], label='Temperature $T$')
axes[0].set_xlabel(f'PC1 ({var_explained[0]*100:.1f}% variance)')
axes[0].set_ylabel(f'PC2 ({var_explained[1]*100:.1f}% variance)')
axes[0].set_title('PCA: Ising configurations colored by temperature')

pc1_vs_T = []
for T in T_range:
    mask = np.abs(T_data - T) < 0.05
    if mask.sum() > 0:
        pc1_vs_T.append((T, np.mean(X_pca[mask, 0])))

T_arr, pc1_arr = zip(*pc1_vs_T)
axes[1].plot(T_arr, pc1_arr, 'o-', color='blue', markersize=6)
axes[1].axvline(2.269, color='red', linestyle='--', label=r'$T_c \approx 2.269$')
axes[1].set_xlabel('Temperature $T$')
axes[1].set_ylabel('Mean PC1')
axes[1].set_title('First principal component vs temperature')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('ising_pca')
plt.show()
