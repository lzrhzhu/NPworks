"""Ground and first excited harmonic-oscillator states by imaginary time."""
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

x_max = 6.0
n_intervals = 200
dtau = 0.001
n_steps = 10000
dx = 2.0 * x_max / n_intervals
x = np.linspace(-x_max, x_max, n_intervals + 1)[1:-1]
potential = 0.5 * x ** 2
main = 1.0 / dx ** 2 + potential
offdiag = -0.5 / dx ** 2


def apply_hamiltonian(psi):
    result = main * psi
    result[:-1] += offdiag * psi[1:]
    result[1:] += offdiag * psi[:-1]
    return result


def normalize(psi):
    return psi / np.sqrt(np.sum(np.abs(psi) ** 2) * dx)


def energy(psi):
    return float(np.sum(np.conjugate(psi) * apply_hamiltonian(psi)).real * dx)


psi0 = normalize(np.exp(-0.5 * (x - 1.0) ** 2))
times = [0.0]
energies = [energy(psi0)]
for step in range(1, n_steps + 1):
    psi0 = normalize(psi0 - dtau * apply_hamiltonian(psi0))
    if step % 100 == 0:
        times.append(step * dtau)
        energies.append(energy(psi0))

psi1 = normalize(x * np.exp(-0.25 * x ** 2))
for _ in range(n_steps):
    psi1 = psi1 - dtau * apply_hamiltonian(psi1)
    psi1 = psi1 - np.sum(psi0 * psi1) * dx * psi0
    psi1 = normalize(psi1)

ground_energy = energy(psi0)
excited_energy = energy(psi1)
print("Initial energy:", energies[0])
print("Ground-state energy:", ground_energy)
print("First-excited-state energy:", excited_energy)

ground_exact = np.pi ** (-0.25) * np.exp(-0.5 * x ** 2)
excited_exact = np.sqrt(2.0) * x * ground_exact

fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0))
ax = axes[0]
ax.plot(times, energies, color='tab:blue')
ax.axhline(0.5, color='black', linestyle='--', label='Exact E0=0.5')
ax.set_xlabel('tau (natural units)')
ax.set_ylabel('Energy expectation (natural units)')
ax.set_title('Imaginary-Time Convergence')
ax.legend(frameon=False)
ax.minorticks_on()
ax.text(0.03, 0.94, '(a)', transform=ax.transAxes)

ax = axes[1]
ax.plot(x, psi0, color='tab:blue', label=f'Ground, E={ground_energy:.6f}')
ax.plot(x, ground_exact, color='tab:blue', linestyle='--', label='Ground exact')
ax.plot(x, psi1, color='tab:orange', linestyle='-.', label=f'Excited, E={excited_energy:.6f}')
ax.plot(x, excited_exact, color='tab:orange', linestyle=':', label='Excited exact')
ax.set_xlim(-4.0, 4.0)
ax.set_xlabel('x (natural units)')
ax.set_ylabel('psi(x) (natural units)')
ax.set_title('Converged Eigenstates')
ax.legend(frameon=False, fontsize=8)
ax.minorticks_on()
ax.text(0.03, 0.94, '(b)', transform=ax.transAxes)

plt.tight_layout()
plt.suptitle('imaginary_time_harmonic')
plt.show()
