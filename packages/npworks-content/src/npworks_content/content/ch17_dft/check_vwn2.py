from pyscf.dft import libxc
import numpy as np

print("Exchange only (lda,):")
for rho in [0.01, 0.1, 0.5, 1.0]:
    exc, vxc, _, _ = libxc.eval_xc("lda,", np.array([rho]), spin=0)
    print(f"  rho={rho:.2f}: eps_x={exc[0]:.8f}")

print("\nCorrelation only (vwn):")
for rho in [0.01, 0.1, 0.5, 1.0]:
    exc, vxc, _, _ = libxc.eval_xc(",vwn", np.array([rho]), spin=0)
    print(f"  rho={rho:.2f}: eps_c={exc[0]:.8f}")

print("\nExchange + correlation (lda,vwn):")
for rho in [0.01, 0.1, 0.5, 1.0]:
    exc, vxc, _, _ = libxc.eval_xc("lda,vwn", np.array([rho]), spin=0)
    print(f"  rho={rho:.2f}: eps_xc={exc[0]:.8f}")

# Also check with pure correlation functional names
print("\nOther correlation only:")
for xc in [",vwn", ",vwn5", ",pyvwn"]:
    try:
        exc, _, _, _ = libxc.eval_xc(xc, np.array([0.5]), spin=0)
        print(f"  {xc:10s} at rho=0.5: eps_c={exc[0]:.8f}")
    except:
        print(f"  {xc:10s}: not available")
