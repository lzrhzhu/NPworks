"""德拜屏蔽（Debye shielding）。"""
import numpy as np
import matplotlib.pyplot as plt


lambda_D = 1.0
r = np.linspace(0.05, 8, 400)
phi_bare = 1.0 / r
phi_shielded = (1.0 / r) * np.exp(-r / lambda_D)

# --- 图1：势能曲线对比 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(r, phi_bare, 'r--', linewidth=2, label=r'裸势 $1/r$（真空）')
ax.plot(r, phi_shielded, 'b-', linewidth=2.2, label=r'屏蔽势 $(1/r)e^{-r/\lambda_D}$')
ax.axvline(lambda_D, color='gray', linestyle=':', linewidth=1.5)
ax.text(lambda_D + 0.1, ax.get_ylim()[1] * 0.6, r'$\lambda_D$', rotation=90, va='top')
ax.set_xlabel(r'$r / \lambda_D$'); ax.set_ylabel(r'$\phi(r)$')
ax.set_title('德拜屏蔽：势在 ~λD 内被指数压抑')
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('debye_shielding')

# --- 图2：半对数图 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(r, phi_bare, 'r--', linewidth=2, label='裸势 $1/r$')
ax.semilogy(r, phi_shielded, 'b-', linewidth=2.2, label=r'屏蔽势 $\propto e^{-r/\lambda_D}/r$')
ax.set_xlabel(r'$r / \lambda_D$'); ax.set_ylabel(r'$\phi(r)$（对数）')
ax.set_title('半对数图：屏蔽势呈直线（指数衰减）')
ax.legend(); ax.grid(True, alpha=0.3, which='both')
plt.tight_layout()
plt.suptitle('debye_shielding_log')

print("01_debye_shielding.py done")

plt.show()
