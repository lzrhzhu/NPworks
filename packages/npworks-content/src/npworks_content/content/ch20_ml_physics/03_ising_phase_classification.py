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


def ising_2d_mc(L, T, N_therm, N_relax, seed=42):
    rng = np.random.default_rng(seed)
    beta = 1.0 / T
    s = rng.choice([-1, 1], size=(L, L)).astype(np.int8)
    ii, jj = np.indices((L, L))
    red = ((ii + jj) % 2 == 0)

    def sweep():
        for color in (red, ~red):
            nb = (np.roll(s, 1, 0) + np.roll(s, -1, 0) +
                  np.roll(s, 1, 1) + np.roll(s, -1, 1))
            dE = 2 * s * nb
            random_values = rng.random((L, L))
            accept = (dE <= 0) | (random_values < np.exp(-beta * np.maximum(dE, 0)))
            s[color & accept] = -s[color & accept]

    for _ in range(N_therm):
        sweep()
    for _ in range(N_relax):
        sweep()

    # 哈密顿量在全局自旋翻转下不变；随机翻转可消除有限采样的磁化符号偏置。
    if rng.random() < 0.5:
        s *= -1
    return s.copy()


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


L = 16
Tc = 2.269
T_range = np.linspace(1.5, 3.5, 15)
n_samples_per_T = 20

print("Generating Ising configurations...")
all_configs = []
all_temps = []
all_labels = []
all_temp_indices = []

for tidx, T in enumerate(T_range):
    for sample_idx in range(n_samples_per_T):
        config = ising_2d_mc(
            L, T, N_therm=800, N_relax=200,
            seed=42 + tidx * 1000 + sample_idx,
        )
        all_configs.append(config.flatten().astype(float))
        all_temps.append(T)
        all_labels.append(0 if T < Tc else 1)
        all_temp_indices.append(tidx)
    print(f"  T={T:.2f} done ({tidx + 1}/{len(T_range)})")

X = np.array(all_configs)
y = np.array(all_labels)
T_data = np.array(all_temps)
temp_indices = np.array(all_temp_indices)

# 每个温度分别按 7:3 划分，避免某个温度在测试集中样本过少。
split_rng = np.random.default_rng(2026)
train_idx = []
test_idx = []
for tidx in range(len(T_range)):
    indices = np.flatnonzero(temp_indices == tidx)
    indices = split_rng.permutation(indices)
    split = int(0.7 * len(indices))
    train_idx.extend(indices[:split])
    test_idx.extend(indices[split:])

train_idx = np.array(train_idx)
test_idx = np.array(test_idx)
X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]
T_test = T_data[test_idx]

rng = np.random.default_rng(42)
n_input = L * L
n_hidden = 64
lr = 0.003
epochs = 1200

W1 = rng.normal(0, np.sqrt(2.0 / n_input), size=(n_input, n_hidden))
b1 = np.zeros((1, n_hidden))
W2 = rng.normal(0, np.sqrt(2.0 / n_hidden), size=(n_hidden, 1))
b2 = np.zeros((1, 1))
params = [W1, b1, W2, b2]
first_moment = [np.zeros_like(p) for p in params]
second_moment = [np.zeros_like(p) for p in params]

losses = []
for epoch in range(1, epochs + 1):
    z1 = X_train @ W1 + b1
    a1 = np.maximum(0, z1)
    z2 = a1 @ W2 + b2
    y_prob = sigmoid(z2)

    eps = 1e-8
    loss = -np.mean(y_train[:, None] * np.log(y_prob + eps) +
                    (1 - y_train[:, None]) * np.log(1 - y_prob + eps))
    losses.append(loss)

    dz2 = (y_prob - y_train[:, None]) / len(y_train)
    dW2 = a1.T @ dz2
    db2 = np.sum(dz2, axis=0, keepdims=True)
    dz1 = (dz2 @ W2.T) * (z1 > 0)
    dW1 = X_train.T @ dz1
    db1 = np.sum(dz1, axis=0, keepdims=True)
    grads = [dW1, db1, dW2, db2]

    beta1, beta2 = 0.9, 0.999
    for i, (param, grad) in enumerate(zip(params, grads)):
        first_moment[i] = beta1 * first_moment[i] + (1 - beta1) * grad
        second_moment[i] = beta2 * second_moment[i] + (1 - beta2) * grad**2
        m_hat = first_moment[i] / (1 - beta1**epoch)
        v_hat = second_moment[i] / (1 - beta2**epoch)
        param -= lr * m_hat / (np.sqrt(v_hat) + 1e-8)

z1_test = X_test @ W1 + b1
y_pred_prob = sigmoid(np.maximum(0, z1_test) @ W2 + b2).flatten()
y_pred = (y_pred_prob > 0.5).astype(int)
overall_acc = np.mean(y_pred == y_test)
print(f"Overall accuracy: {overall_acc:.4f}")

mean_probability = []
probability_sem = []
accuracy_per_T = []
accuracy_sem = []
for T in T_range:
    mask = np.isclose(T_test, T)
    probabilities = y_pred_prob[mask]
    correct = (y_pred[mask] == y_test[mask]).astype(float)
    mean_probability.append(np.mean(probabilities))
    probability_sem.append(np.std(probabilities, ddof=1) / np.sqrt(len(probabilities)))
    accuracy_per_T.append(np.mean(correct))
    accuracy_sem.append(np.std(correct, ddof=1) / np.sqrt(len(correct)))

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].errorbar(T_range, mean_probability, yerr=probability_sem,
                 fmt='o-', capsize=3, label='Test-set mean')
axes[0].axvline(Tc, color='black', linestyle='--', label=r'$T_c \approx 2.269$')
axes[0].set_xlabel('Temperature $T$ (reduced units)')
axes[0].set_ylabel('Predicted disordered-phase probability')
axes[0].set_title('(a) Classifier output')
axes[0].set_ylim(-0.05, 1.05)
axes[0].legend(frameon=False, loc='best')
axes[0].minorticks_on()

axes[1].errorbar(T_range, accuracy_per_T, yerr=accuracy_sem,
                 fmt='s-', capsize=3, color='tab:orange', label='Test accuracy')
axes[1].axvline(Tc, color='black', linestyle='--', label=r'$T_c \approx 2.269$')
axes[1].set_xlabel('Temperature $T$ (reduced units)')
axes[1].set_ylabel('Classification accuracy')
axes[1].set_title('(b) Accuracy by temperature')
axes[1].set_ylim(-0.05, 1.05)
axes[1].legend(frameon=False, loc='best')
axes[1].minorticks_on()
plt.tight_layout()
plt.suptitle('ml_physics_ising_phase_classification')

fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(losses)
ax.set_xlabel('Epoch')
ax.set_ylabel('Cross-entropy loss')
ax.set_title('Training loss')
ax.minorticks_on()
plt.tight_layout()
plt.suptitle('ml_physics_ising_classification_loss')
print("03_ising_phase_classification.py done")

plt.show()
