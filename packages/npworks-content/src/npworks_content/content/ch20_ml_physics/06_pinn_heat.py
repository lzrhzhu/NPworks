import numpy as np
import matplotlib.pyplot as plt
import torch

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 9, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'lines.markersize': 5,
    'axes.grid': False, 'axes.unicode_minus': False,
})

torch.manual_seed(42)
np.random.seed(42)
torch.set_default_dtype(torch.float64)


class PINN(torch.nn.Module):
    def __init__(self, n_hidden=32):
        super().__init__()
        self.network = torch.nn.Sequential(
            torch.nn.Linear(2, n_hidden), torch.nn.Tanh(),
            torch.nn.Linear(n_hidden, n_hidden), torch.nn.Tanh(),
            torch.nn.Linear(n_hidden, 1),
        )

    def forward(self, X):
        return self.network(X)


def residual(model, X):
    X = X.clone().detach().requires_grad_(True)
    u = model(X)
    grad_u = torch.autograd.grad(u, X, torch.ones_like(u), create_graph=True)[0]
    u_t = grad_u[:, 1:2]
    u_x = grad_u[:, 0:1]
    grad_ux = torch.autograd.grad(u_x, X, torch.ones_like(u_x), create_graph=True)[0]
    u_xx = grad_ux[:, 0:1]
    return u_t - u_xx


N_f, N_0, N_b = 1000, 100, 100
rng = np.random.default_rng(42)
xt_f = torch.tensor(rng.uniform(0, 1, (N_f, 2)))
x_0 = torch.linspace(0, 1, N_0)[:, None]
xt_0 = torch.cat([x_0, torch.zeros_like(x_0)], dim=1)
T_ic = torch.sin(torch.pi * x_0)
t_b = torch.linspace(0, 1, N_b)[:, None]
xt_L = torch.cat([torch.zeros_like(t_b), t_b], dim=1)
xt_R = torch.cat([torch.ones_like(t_b), t_b], dim=1)

model = PINN(n_hidden=32)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
epochs = 4000
losses = []
for epoch in range(epochs):
    optimizer.zero_grad()
    loss_f = torch.mean(residual(model, xt_f) ** 2)
    loss_ic = torch.mean((model(xt_0) - T_ic) ** 2)
    loss_bc = torch.mean(model(xt_L) ** 2) + torch.mean(model(xt_R) ** 2)
    loss = loss_f + 10 * loss_ic + 10 * loss_bc
    loss.backward()
    optimizer.step()
    losses.append(float(loss.detach()))
    if epoch % 1000 == 0:
        print(f'Epoch {epoch}: loss={losses[-1]:.6e}')

x_plot = np.linspace(0, 1, 100)
t_plot_vals = [0.0, 0.2, 0.5, 1.0]
fig, ax = plt.subplots(figsize=(8, 5))
for t_val in t_plot_vals:
    xt_in = torch.tensor(np.column_stack([x_plot, np.full_like(x_plot, t_val)]))
    T_nn = model(xt_in).detach().numpy().ravel()
    T_exact = np.exp(-np.pi**2 * t_val) * np.sin(np.pi * x_plot)
    ax.plot(x_plot, T_exact, '-', linewidth=1.8, label=f'$t={t_val:.1f}$ exact')
    ax.plot(x_plot, T_nn, '--', linewidth=1.4, label=f'$t={t_val:.1f}$ PINN')
ax.set_xlabel('$x$ (dimensionless)'); ax.set_ylabel('$T(x,t)$ (dimensionless)')
ax.set_title('PINN solution and exact solution'); ax.legend(frameon=False, ncol=2); ax.minorticks_on()
plt.tight_layout(); plt.suptitle('ml_physics_pinn_heat')

fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(losses)
ax.set_xlabel('Epoch'); ax.set_ylabel('Total loss'); ax.set_title('PINN training loss'); ax.minorticks_on()
plt.tight_layout(); plt.suptitle('ml_physics_pinn_loss')

with torch.no_grad():
    test = torch.tensor(np.column_stack([np.tile(x_plot, len(t_plot_vals)),
                                         np.repeat(t_plot_vals, len(x_plot))]))
    pred = model(test).numpy().ravel()
exact = np.concatenate([np.exp(-np.pi**2 * t) * np.sin(np.pi * x_plot) for t in t_plot_vals])
print(f'Final loss: {losses[-1]:.6e}')
print(f'Test-grid RMSE: {np.sqrt(np.mean((pred - exact)**2)):.6e}')
print('06_pinn_heat.py done')
plt.show()
