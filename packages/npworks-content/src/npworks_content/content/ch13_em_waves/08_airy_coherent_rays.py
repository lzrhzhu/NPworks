"""
Coherent ray summing vs the closed-form Airy formula for a single dielectric
slab (Fabry-Perot). Each multiply-reflected ray carries a complex amplitude
(with phase); summing them reproduces the Airy result, which is exactly the
TMM transmission. Partial sums (a finite number of transmitted beams) converge
to the full wave result -- showing that coherent ray tracing == TMM.
"""
import numpy as np
import matplotlib.pyplot as plt

n0 = 1.0
n = 2.0
ns = 1.0
d = 1.0                                # slab thickness (arb. units)

# Fresnel field coefficients (normal incidence)
t1 = 2 * n0 / (n0 + n)                 # air -> slab
t2 = 2 * n / (n + ns)                  # slab -> air
r1p = (n - n0) / (n + n0)              # reflection at iface 1 from inside
r2 = (n - ns) / (n + ns)               # reflection at iface 2 from inside

lams = np.linspace(0.4, 1.6, 800) * d


def T_exact(lam):
    delta = 2 * np.pi * n * d / lam
    amp = t1 * t2 * np.exp(1j * delta)
    rt = r1p * r2 * np.exp(2j * delta)
    t = amp / (1 - rt)                 # closed-form geometric series
    return (ns / n0) * np.abs(t) ** 2


def T_partial(lam, mmax):
    delta = 2 * np.pi * n * d / lam
    direct = t1 * t2 * np.exp(1j * delta)
    rt = r1p * r2 * np.exp(2j * delta)
    tot = np.zeros_like(delta, dtype=complex)
    for m in range(mmax + 1):          # sum first mmax+1 transmitted beams
        tot += direct * rt ** m
    return (ns / n0) * np.abs(tot) ** 2


T_ex = T_exact(lams)

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(lams / d, T_ex, "k-", lw=2, label="exact (Airy = TMM)")
for mmax in [0, 1, 2, 5]:
    ax.plot(lams / d, T_partial(lams, mmax),
            label=f"ray sum, {mmax + 1} transmitted beams")
ax.set_xlabel("λ / d")
ax.set_ylabel("Transmittance T")
ax.set_title("Coherent ray summing converges to the wave (TMM) result")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1.1)

plt.suptitle('airy_coherent_rays')
plt.show()
print("08_airy_coherent_rays.py done")
