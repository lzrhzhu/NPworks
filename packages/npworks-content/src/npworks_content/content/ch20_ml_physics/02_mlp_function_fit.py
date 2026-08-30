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


def target_func(x):
    return np.sin(2 * x) + 0.3 * np.cos(5 * x)


np.random.seed(42)

N_hidden = 32
lr = 0.01
epochs = 3000

x_train = np.linspace(-2, 2, 200)
y_train = target_func(x_train)

np.random.seed(42)
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
    X = x_train.reshape(-1, 1)

    z1 = X @ W1 + b1
    a1 = tanh(z1)
    z2 = a1 @ W2 + b2
    a2 = tanh(z2)
    z3 = a2 @ W3 + b3
    y_pred = z3

    loss = np.mean((y_pred.flatten() - y_train) ** 2)
    losses.append(loss)

    dy = 2 * (y_pred - y_train.reshape(-1, 1)) / len(y_train)
    dW3 = a2.T @ dy
    db3 = np.sum(dy, axis=0, keepdims=True)

    da2 = dy @ W3.T
    dz2 = da2 * tanh_deriv(z2)
    dW2 = a1.T @ dz2
    db2 = np.sum(dz2, axis=0, keepdims=True)

    da1 = dz2 @ W2.T
    dz1 = da1 * tanh_deriv(z1)
    dW1 = X.T @ dz1
    db1 = np.sum(dz1, axis=0, keepdims=True)

    W1 -= lr * dW1
    b1 -= lr * db1
    W2 -= lr * dW2
    b2 -= lr * db2
    W3 -= lr * dW3
    b3 -= lr * db3

x_test = np.linspace(-2, 2, 500)
X_test = x_test.reshape(-1, 1)
z1 = X_test @ W1 + b1
a1 = tanh(z1)
z2 = a1 @ W2 + b2
a2 = tanh(z2)
z3 = a2 @ W3 + b3
y_nn = z3.flatten()

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(x_train, y_train, s=10, c='gray', alpha=0.5, label='Training data')
ax.plot(x_test, target_func(x_test), 'b-', label='Target function', linewidth=2)
ax.plot(x_test, y_nn, 'r--', label='Neural network', linewidth=2)
ax.set_title('Function approximation'); ax.legend(frameon=False); ax.minorticks_on()
ax.set_xlabel('$x$'); ax.set_ylabel('$y$')
plt.tight_layout(); plt.suptitle('ml_physics_mlp_function_fit')
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(losses); ax.set_xlabel('Epoch'); ax.set_ylabel('Loss (MSE)')
ax.set_title('Training loss'); ax.minorticks_on()
plt.tight_layout(); plt.suptitle('ml_physics_mlp_loss')
print("02_mlp_function_fit.py done")

plt.show()
