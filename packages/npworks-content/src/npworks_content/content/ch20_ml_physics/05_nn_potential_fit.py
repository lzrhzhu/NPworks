import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'lines.markersize': 5,
    'axes.grid': False, 'axes.unicode_minus': False,
})


def lj_potential(r, epsilon=1.0, sigma=1.0):
    r_safe = np.maximum(r, 0.5)
    return 4 * epsilon * ((sigma / r_safe)**12 - (sigma / r_safe)**6)


rng = np.random.default_rng(42)
N_hidden = 64
lr = 0.002
epochs = 8000

# 排斥壁曲率较大，因此在短程区加密采样。
r_train = np.unique(np.concatenate([
    np.linspace(0.9, 1.35, 300),
    np.linspace(1.35, 3.0, 300),
]))
r_min = 2 ** (1 / 6)
E_shift = lj_potential(np.array([r_min]))[0]
x_train = r_train[:, None]
y_train = (lj_potential(r_train) - E_shift)[:, None]

x_mean, x_std = x_train.mean(), x_train.std()
y_mean, y_std = y_train.mean(), y_train.std()
X_norm = (x_train - x_mean) / x_std
Y_norm = (y_train - y_mean) / y_std

W1 = rng.normal(0, np.sqrt(1.0), size=(1, N_hidden))
b1 = np.zeros((1, N_hidden))
W2 = rng.normal(0, np.sqrt(1.0 / N_hidden), size=(N_hidden, N_hidden))
b2 = np.zeros((1, N_hidden))
W3 = rng.normal(0, np.sqrt(1.0 / N_hidden), size=(N_hidden, 1))
b3 = np.zeros((1, 1))
params = [W1, b1, W2, b2, W3, b3]
first_moment = [np.zeros_like(p) for p in params]
second_moment = [np.zeros_like(p) for p in params]

losses = []
for epoch in range(1, epochs + 1):
    z1 = X_norm @ W1 + b1
    a1 = np.tanh(z1)
    z2 = a1 @ W2 + b2
    a2 = np.tanh(z2)
    y_pred_norm = a2 @ W3 + b3
    residual = y_pred_norm - Y_norm
    losses.append(np.mean(residual**2) * y_std**2)

    dy = 2 * residual / len(Y_norm)
    dW3 = a2.T @ dy
    db3 = np.sum(dy, axis=0, keepdims=True)
    dz2 = (dy @ W3.T) * (1 - a2**2)
    dW2 = a1.T @ dz2
    db2 = np.sum(dz2, axis=0, keepdims=True)
    dz1 = (dz2 @ W2.T) * (1 - a1**2)
    dW1 = X_norm.T @ dz1
    db1 = np.sum(dz1, axis=0, keepdims=True)
    grads = [dW1, db1, dW2, db2, dW3, db3]

    beta1, beta2 = 0.9, 0.999
    for i, (param, grad) in enumerate(zip(params, grads)):
        first_moment[i] = beta1 * first_moment[i] + (1 - beta1) * grad
        second_moment[i] = beta2 * second_moment[i] + (1 - beta2) * grad**2
        m_hat = first_moment[i] / (1 - beta1**epoch)
        v_hat = second_moment[i] / (1 - beta2**epoch)
        param -= lr * m_hat / (np.sqrt(v_hat) + 1e-8)

r_test = np.linspace(0.85, 3.5, 1000)
X_test_norm = (r_test[:, None] - x_mean) / x_std
a1 = np.tanh(X_test_norm @ W1 + b1)
a2 = np.tanh(a1 @ W2 + b2)
E_nn = (a2 @ W3 + b3).ravel() * y_std + y_mean
E_exact = lj_potential(r_test) - E_shift
abs_error = np.abs(E_nn - E_exact)
inside = (r_test >= 0.9) & (r_test <= 3.0)
outside = r_test > 3.0
train_rmse = np.sqrt(np.mean((E_nn[inside] - E_exact[inside])**2))
outside_rmse = np.sqrt(np.mean((E_nn[outside] - E_exact[outside])**2))
print(f'Training-range RMSE: {train_rmse:.6f}')
print(f'Extrapolation RMSE (r > 3): {outside_rmse:.6f}')

fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
axes[0].plot(r_test, E_exact, '-', label='LJ potential (exact)')
axes[0].plot(r_test, E_nn, '--', label='Neural network fit')
axes[0].axvspan(0.9, 3.0, color='0.9', zorder=-1, label='Training interval')
axes[0].set_ylabel(r'$[V(r)-V(r_{\min})]/\epsilon$')
axes[0].set_title('(a) Potential')
axes[0].set_ylim(-0.2, 2.0)
axes[0].legend(frameon=False, loc='best')
axes[0].minorticks_on()
axes[1].semilogy(r_test, np.maximum(abs_error, 1e-8), '-.')
axes[1].axvspan(0.9, 3.0, color='0.9', zorder=-1)
axes[1].set_xlabel(r'$r/\sigma$')
axes[1].set_ylabel(r'Absolute error ($\epsilon$)')
axes[1].set_title('(b) Pointwise error')
axes[1].minorticks_on()
plt.tight_layout()
plt.suptitle('ml_physics_nn_potential_fit')

fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(losses)
ax.set_xlabel('Epoch')
ax.set_ylabel(r'Training MSE ($\epsilon^2$)')
ax.set_title('Training loss')
ax.minorticks_on()
plt.tight_layout()
plt.suptitle('ml_physics_nn_potential_loss')
print('05_nn_potential_fit.py done')
plt.show()
