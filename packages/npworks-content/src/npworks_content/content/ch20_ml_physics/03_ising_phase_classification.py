import numpy as np
import matplotlib.pyplot as plt


def ising_2d_mc(L, T, N_therm, N_measure, seed=42):
    rng = np.random.default_rng(seed)
    beta = 1.0 / T
    s = np.ones((L, L), dtype=np.int8)
    ii, jj = np.indices((L, L))
    red = ((ii + jj) % 2 == 0)

    def sweep():
        for color in (red, ~red):
            nb = (np.roll(s, 1, 0) + np.roll(s, -1, 0) +
                  np.roll(s, 1, 1) + np.roll(s, -1, 1))
            dE = 2 * s * nb
            r = rng.random((L, L))
            accept = (dE <= 0) | (r < np.exp(-beta * np.maximum(dE, 0)))
            s[color & accept] = -s[color & accept]

    for _ in range(N_therm):
        sweep()
    for _ in range(N_measure):
        sweep()
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

import os
_d = os.path.dirname(os.path.abspath(__file__))
for _ in range(10):
    if os.path.isdir(os.path.join(_d, "markdown")):
        IMG_DIR = os.path.join(_d, "markdown", "images", "ch21"); break
    _d = os.path.dirname(_d)
else:
    IMG_DIR = os.path.join(os.path.expanduser("~"), "npworks_figures", "ch21"); os.makedirs(IMG_DIR, exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(bin_centers, accuracy_per_T, 'o-', markersize=8)
ax.axvline(2.269, color='red', linestyle='--', label=r'$T_c \approx 2.269$')
ax.set_xlabel('Temperature $T$'); ax.set_ylabel('Classification accuracy')
ax.set_title('Supervised Learning: Phase Classification'); ax.legend(); ax.grid(True, alpha=0.3); ax.set_ylim(0, 1.05)
plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, "ch21_ml_physics_ising_phase_classification.png"), dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(losses); ax.set_xlabel('Epoch'); ax.set_ylabel('Cross-entropy loss')
ax.set_title('Training loss'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, "ch21_ml_physics_ising_classification_loss.png"), dpi=130); plt.close(fig)
print("03_ising_phase_classification.py done")
