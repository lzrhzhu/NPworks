"""德拜屏蔽（Debye shielding）。

等离子体中电子在外来电荷周围形成屏蔽云，使电势按
  phi(r) = (Q / 4*pi*eps0*r) * exp(-r / lambda_D)
指数衰减（而非真空的 1/r）。德拜长度 lambda_D = sqrt(eps0 kT / (n e^2))
是屏蔽的空间尺度，也是等离子体最根本的集体效应之一。
（这里用归一化单位 Q/4*pi*eps0 = 1，lambda_D = 1。）
"""
import numpy as np
import matplotlib.pyplot as plt

lambda_D = 1.0
r = np.linspace(0.05, 8, 400)

phi_bare = 1.0 / r                       # 真空库仑势
phi_shielded = (1.0 / r) * np.exp(-r / lambda_D)   # 屏蔽势

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

# 左：势能曲线对比
axes[0].plot(r, phi_bare, 'r--', linewidth=2, label=r'裸势 $1/r$（真空）')
axes[0].plot(r, phi_shielded, 'b-', linewidth=2.2,
             label=r'屏蔽势 $(1/r)e^{-r/\lambda_D}$')
axes[0].axvline(lambda_D, color='gray', linestyle=':', linewidth=1.5)
axes[0].text(lambda_D + 0.1, axes[0].get_ylim()[1] * 0.6,
             r'$\lambda_D$（德拜长度）', rotation=90, va='top')
axes[0].set_xlabel('$r / \\lambda_D$')
axes[0].set_ylabel(r'$\phi(r)$')
axes[0].set_title('德拜屏蔽：势在 ~λD 内被指数压抑')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 右：对数纵轴，清楚看到指数衰减
axes[1].semilogy(r, phi_bare, 'r--', linewidth=2, label='裸势 $1/r$')
axes[1].semilogy(r, phi_shielded, 'b-', linewidth=2.2,
                 label=r'屏蔽势 $\propto e^{-r/\lambda_D}/r$')
axes[1].set_xlabel('$r / \\lambda_D$')
axes[1].set_ylabel(r'$\phi(r)$（对数）')
axes[1].set_title('半对数图：屏蔽势呈直线（指数衰减）')
axes[1].legend()
axes[1].grid(True, alpha=0.3, which='both')

plt.tight_layout()
plt.suptitle('debye_shielding')
plt.show()
print("01_debye_shielding.py done")
