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


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


L = 16
Tc = 2.269
T_range = np.linspace(1.5, 3.5, 15)
n_samples_per_T = 15

print("Generating Ising configurations...")
all_configs = []
all_temps = []
all_labels = []

for tidx, T in enumerate(T_range):
    for s_idx in range(n_samples_per_T):
        config = ising_2d_mc(L, T, N_therm=500, N_measure=300,
                             seed=42 + tidx * 100 + s_idx)
        all_configs.append(config.flatten().astype(float))
        all_temps.append(T)
        all_labels.append(0 if T < Tc else 1)
    print(f"  T={T:.2f} done ({(tidx+1)}/{len(T_range)})")

X = np.array(all_configs)
y = np.array(all_labels)
T_data = np.array(all_temps)

N_data = len(X)
indices = np.random.permutation(N_data)
split = int(0.7 * N_data)
train_idx, test_idx = indices[:split], indices[split:]
X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]
T_train, T_test = T_data[train_idx], T_data[test_idx]

np.random.seed(42)
n_input = L * L
n_hidden = 32
lr = 0.01
epochs = 300

W1 = np.random.randn(n_input, n_hidden) * 0.01
b1 = np.zeros((1, n_hidden))
W2 = np.random.randn(n_hidden, 1) * 0.01
b2 = np.zeros((1, 1))

losses = []
for epoch in range(epochs):
    z1 = X_train @ W1 + b1
    a1 = np.maximum(0, z1)
    z2 = a1 @ W2 + b2
    y_prob = sigmoid(z2)

    eps = 1e-8
    loss = -np.mean(y_train.reshape(-1, 1) * np.log(y_prob + eps) +
                     (1 - y_train.reshape(-1, 1)) * np.log(1 - y_prob + eps))
    losses.append(loss)

    dz2 = y_prob - y_train.reshape(-1, 1)
    dW2 = a1.T @ dz2 / len(y_train)
    db2 = np.mean(dz2, axis=0, keepdims=True)

    da1 = dz2 @ W2.T
    dz1 = da1 * (z1 > 0).astype(float)
    dW1 = X_train.T @ dz1 / len(y_train)
    db1 = np.mean(dz1, axis=0, keepdims=True)

    W1 -= lr * dW1
    b1 -= lr * db1
    W2 -= lr * dW2
    b2 -= lr * db2

z1_test = X_test @ W1 + b1
a1_test = np.maximum(0, z1_test)
z2_test = a1_test @ W2 + b2
y_pred_prob = sigmoid(z2_test).flatten()
y_pred = (y_pred_prob > 0.5).astype(int)

overall_acc = np.mean(y_pred == y_test)
print(f"Overall accuracy: {overall_acc:.4f}")

temp_bins = np.linspace(1.5, 3.5, 11)
accuracy_per_T = []
bin_centers = []
for i in range(len(temp_bins) - 1):
    mask = (T_test >= temp_bins[i]) & (T_test < temp_bins[i+1])
    if mask.sum() > 0:
        accuracy_per_T.append(np.mean(y_pred[mask] == y_test[mask]))
        bin_centers.append(0.5 * (temp_bins[i] + temp_bins[i+1]))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(bin_centers, accuracy_per_T, 'o-', markersize=8)
axes[0].axvline(2.269, color='red', linestyle='--', label=r'$T_c \approx 2.269$')
axes[0].set_xlabel('Temperature $T$')
axes[0].set_ylabel('Classification accuracy')
axes[0].set_title('Supervised Learning: Phase Classification')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim(0, 1.05)

axes[1].semilogy(losses)
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Cross-entropy loss')
axes[1].set_title('Training loss')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('ising_phase_classification')
plt.show()
