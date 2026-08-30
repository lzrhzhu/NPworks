"""Hydrogen s-state energies from the radial Schrödinger equation."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh_tridiagonal

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

r_min = 1.0e-6
r_max = 30.0
n_intervals = 500
r_full = np.linspace(r_min, r_max, n_intervals + 1)
dr = r_full[1] - r_full[0]
r = r_full[1:-1]
main = 1.0 / dr ** 2 - 1.0 / r
offdiag = np.full(n_intervals - 2, -0.5 / dr ** 2)
energies, states = eigh_tridiagonal(main, offdiag, select='i', select_range=(0, 2))
exact = np.array([-0.5, -0.125, -1.0 / 18.0])

print("Hydrogen radial energies:", energies)
print("Relative errors:", np.abs((energies - exact) / exact))

fig, ax = plt.subplots()
styles = ['-', '--', '-.']
for index in range(3):
    radial = states[:, index]
    anchor = np.argmax(np.abs(radial))
    radial *= np.sign(radial[anchor]) or 1.0
    radial /= np.sqrt(np.trapz(radial ** 2, r))
    ax.plot(r, radial, linestyle=styles[index],
            label=f'n={index + 1}, E={energies[index]:.5f} a.u.')
ax.set_xlim(0.0, 30.0)
ax.set_xlabel('r (a.u.)')
ax.set_ylabel('u(r) (a.u.)')
ax.set_title('Hydrogen s-State Radial Functions')
ax.legend(frameon=False)
ax.minorticks_on()
plt.tight_layout()
plt.suptitle('hydrogen_radial')
plt.show()
