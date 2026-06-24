import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)


class PINN:
    def __init__(self, n_hidden=16):
        self.nh = n_hidden
        s1 = np.sqrt(2.0 / 2)
        s2 = np.sqrt(2.0 / n_hidden)
        self.W1 = np.random.randn(2, n_hidden) * s1
        self.b1 = np.zeros((1, n_hidden))
        self.W2 = np.random.randn(n_hidden, 1) * s2
        self.b2 = np.zeros((1, 1))

    def _forward(self, X):
        z1 = X @ self.W1 + self.b1
        a1 = np.tanh(z1)
        u = a1 @ self.W2 + self.b2
        return u, a1, z1

    def predict(self, X):
        u, _, _ = self._forward(X)
        return u

    def pde_residual(self, X):
        u, a1, z1 = self._forward(X)
        sech2 = 1 - a1**2

        dz1_dx = np.broadcast_to(self.W1[0:1, :], (X.shape[0], self.nh))
        da1_dx = sech2 * dz1_dx
        du_dx = da1_dx @ self.W2

        dz1_dt = np.broadcast_to(self.W1[1:2, :], (X.shape[0], self.nh))
        da1_dt = sech2 * dz1_dt
        du_dt = da1_dt @ self.W2

        d2a1_dx2 = -2 * a1 * sech2 * dz1_dx**2
        d2u_dx2 = d2a1_dx2 @ self.W2

        return du_dt - d2u_dx2

    def loss(self, xt_f, xt_0, T_ic, xt_L, xt_R):
        res = self.pde_residual(xt_f)
        loss_f = np.mean(res**2)

        u_ic = self.predict(xt_0)
        loss_ic = np.mean((u_ic - T_ic)**2)

        u_L = self.predict(xt_L)
        u_R = self.predict(xt_R)
        loss_bc = np.mean(u_L**2) + np.mean(u_R**2)

        return loss_f + 10 * loss_ic + 10 * loss_bc

    def get_params(self):
        return [self.W1, self.b1, self.W2, self.b2]

    def set_params(self, params):
        self.W1, self.b1, self.W2, self.b2 = params

    def grad_fd(self, xt_f, xt_0, T_ic, xt_L, xt_R, eps=1e-5):
        L0 = self.loss(xt_f, xt_0, T_ic, xt_L, xt_R)
        params = self.get_params()
        grads = []
        for p in params:
            g = np.zeros_like(p)
            it = np.nditer(p, flags=['multi_index'])
            while not it.finished:
                mi = it.multi_index
                old = p[mi]
                p[mi] = old + eps
                Lp = self.loss(xt_f, xt_0, T_ic, xt_L, xt_R)
                g[mi] = (Lp - L0) / eps
                p[mi] = old
                it.iternext()
            grads.append(g)
        return grads


N_f = 500
x_f = np.random.uniform(0, 1, (N_f, 1))
t_f = np.random.uniform(0, 1, (N_f, 1))
xt_f = np.hstack([x_f, t_f])

N_0 = 50
x_0 = np.linspace(0, 1, N_0).reshape(-1, 1)
xt_0 = np.hstack([x_0, np.zeros_like(x_0)])
T_ic = np.sin(np.pi * x_0)

N_b = 50
t_b = np.linspace(0, 1, N_b).reshape(-1, 1)
xt_L = np.hstack([np.zeros_like(t_b), t_b])
xt_R = np.hstack([np.ones_like(t_b), t_b])

model = PINN(n_hidden=16)
lr = 0.005
epochs = 4000
losses = []

print(f"Total parameters: {sum(p.size for p in model.get_params())}")

for epoch in range(epochs):
    current_lr = lr * (0.5 ** (epoch // 2000))
    grads = model.grad_fd(xt_f, xt_0, T_ic, xt_L, xt_R)
    params = model.get_params()
    for p, g in zip(params, grads):
        p -= current_lr * g

    L = model.loss(xt_f, xt_0, T_ic, xt_L, xt_R)
    losses.append(L)

    if epoch % 500 == 0:
        print(f"Epoch {epoch}: loss={L:.6f}")

x_plot = np.linspace(0, 1, 80)
t_plot_vals = [0.0, 0.2, 0.5, 1.0]

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

for t_val in t_plot_vals:
    xt_in = np.column_stack([x_plot, np.full_like(x_plot, t_val)])
    T_nn = model.predict(xt_in).flatten()
    T_exact = np.exp(-np.pi**2 * t_val) * np.sin(np.pi * x_plot)

    axes[0].plot(x_plot, T_exact, '-', linewidth=2,
                 label=f'$t={t_val:.1f}$ (exact)')
    axes[0].plot(x_plot, T_nn, '--', linewidth=2,
                 label=f'$t={t_val:.1f}$ (PINN)')

axes[0].set_xlabel('$x$')
axes[0].set_ylabel('$T(x, t)$')
axes[0].set_title('PINN solution vs exact solution')
axes[0].legend(fontsize=7)
axes[0].grid(True, alpha=0.3)

axes[1].semilogy(losses)
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Total loss')
axes[1].set_title('Training loss')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('pinn_heat')
plt.show()
