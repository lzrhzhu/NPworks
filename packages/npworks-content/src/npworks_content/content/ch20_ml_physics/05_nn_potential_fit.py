import numpy as np
import matplotlib.pyplot as plt


def lj_potential(r, epsilon=1.0, sigma=1.0):
    r_safe = np.maximum(r, 0.5)
    return 4 * epsilon * ((sigma / r_safe)**12 - (sigma / r_safe)**6)


np.random.seed(42)

N_hidden = 64
lr = 0.005
epochs = 5000

r_train = np.linspace(0.9, 3.0, 500)
E_train = lj_potential(r_train)

r_min = 1.122
E_shift = lj_potential(np.array([r_min]))[0]
E_train_shifted = E_train - E_shift

x_train = r_train.reshape(-1, 1)
y_train = E_train_shifted.reshape(-1, 1)

x_mean, x_std = x_train.mean(), x_train.std()
X_norm = (x_train - x_mean) / x_std

W1 = np.random.randn(1, N_hidden) * 0.5
b1 = np.zeros((1, N_hidden))
W2 = np.random.randn(N_hidden, N_hidden) * 0.5
b2 = np.zeros((1, N_hidden))
W3 = np.random.randn(N_hidden, 1) * 0.5
b3 = np.zeros((1, 1))


def tanh(x):
    return np.tanh(x)


def tanh_deriv(x):
    return 1 - np.tanh(x) ** 2


losses = []
for epoch in range(epochs):
    z1 = X_norm @ W1 + b1
    a1 = tanh(z1)
    z2 = a1 @ W2 + b2
    a2 = tanh(z2)
    z3 = a2 @ W3 + b3
    y_pred = z3

    loss = np.mean((y_pred - y_train) ** 2)
    losses.append(loss)

    dy = 2 * (y_pred - y_train) / len(y_train)
    dW3 = a2.T @ dy
    db3 = np.sum(dy, axis=0, keepdims=True)

    da2 = dy @ W3.T
    dz2 = da2 * tanh_deriv(z2)
    dW2 = a1.T @ dz2
    db2 = np.sum(dz2, axis=0, keepdims=True)

    da1 = dz2 @ W2.T
    dz1 = da1 * tanh_deriv(z1)
    dW1 = X_norm.T @ dz1
    db1 = np.sum(dz1, axis=0, keepdims=True)

    current_lr = lr * (0.5 ** (epoch // 2000))
    W1 -= current_lr * dW1
    b1 -= current_lr * db1
    W2 -= current_lr * dW2
    b2 -= current_lr * db2
    W3 -= current_lr * dW3
    b3 -= current_lr * db3

r_test = np.linspace(0.85, 3.5, 1000)
X_test_norm = ((r_test.reshape(-1, 1) - x_mean) / x_std)
z1 = X_test_norm @ W1 + b1
a1 = tanh(z1)
z2 = a1 @ W2 + b2
a2 = tanh(z2)
z3 = a2 @ W3 + b3
E_nn = z3.flatten()

E_exact = lj_potential(r_test) - E_shift

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(r_test, E_exact, 'b-', label='LJ potential (exact)', linewidth=2)
axes[0].plot(r_test, E_nn, 'r--', label='Neural network fit', linewidth=2)
axes[0].set_xlabel(r'$r / \sigma$')
axes[0].set_ylabel(r'$V(r) / \epsilon$')
axes[0].set_title('Neural network fit to Lennard-Jones potential')
axes[0].legend()
axes[0].set_ylim(-1.5, 2)
axes[0].grid(True, alpha=0.3)

axes[1].semilogy(losses)
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Loss (MSE)')
axes[1].set_title('Training loss')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('nn_potential_fit')
plt.show()
