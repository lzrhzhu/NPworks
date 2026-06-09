# -*- coding: utf-8 -*-
"""
Validate hand-written HF/DFT programs against PySCF reference calculations.
Ch14: He atom HF (STO-1G + STO-3G), H2 HF/STO-3G
Ch15: He atom DFT (LDA, PBE, B3LYP), H2 DFT/STO-3G potential energy curve
"""
from pyscf import gto, scf, dft
import numpy as np

def bohr_to_ang(R): return R * 0.5291772109

print("=" * 70)
print("PySCF Reference Calculations for Validation")
print("=" * 70)

# ====================================================================
# 1. He atom: HF with STO-3G (matches our ch14 hand-written)
# ====================================================================
print("\n--- 1. He atom HF/STO-3G ---")
mol = gto.M(atom='He 0 0 0', basis='sto-3g', verbose=0)
mf = scf.RHF(mol)
E_hf_sto3g = mf.kernel()
print(f"  HF/STO-3G:  E = {E_hf_sto3g:.6f} Hartree")
print(f"  Our code:   E = -2.300987 Hartree (STO-1G, single Gaussian)")
print(f"  Note: STO-3G vs STO-1G difference expected")

# He atom HF with a single Gaussian (STO-1G equivalent)
# PySCF doesn't have STO-1G built-in, so we use sto-3g and compare integrals
print(f"  PySCF overlap S_11 = {mf.get_ovlp()[0,0]:.6f}")
print(f"  PySCF H_core[0,0] = {(mf.get_hcore())[0,0]:.6f}")
print(f"  PySCF kinetic[0,0] = {mf.get_hcore()[0,0] - mf.get_ovlp()[0,0]*0 + mol.intor('int1e_kin')[0,0]:.6f}")

mol_hf = gto.M(atom='He 0 0 0', basis='sto-3g', verbose=0)
mf_hf = scf.RHF(mol_hf)
E_hf_sto3g = mf_hf.kernel()
H = mf_hf.get_hcore()
S = mf_hf.get_ovlp()
T = mol_hf.intor('int1e_kin')
V = mol_hf.intor('int1e_nuc')
eri = mol_hf.intor('int2e')
print(f"\n  STO-3G integrals (K={S.shape[0]} basis functions):")
print(f"  S = diag: {np.diag(S)}")
print(f"  H_core = {H[0,0]:.6f}")
print(f"  T[0,0] = {T[0,0]:.6f}")
print(f"  V[0,0] = {V[0,0]:.6f}")
print(f"  (11|11) = {eri[0,0,0,0]:.6f}")

# ====================================================================
# 2. He atom: DFT with various functionals, STO-3G
# ====================================================================
print("\n--- 2. He atom DFT/STO-3G ---")
for xc_name, xc_code in [('LDA(SVWN)', 'lda,vwn'), ('PBE', 'pbe,pbe'), ('B3LYP', 'b3lyp')]:
    mol_dft = gto.M(atom='He 0 0 0', basis='sto-3g', verbose=0)
    mf_dft = dft.RKS(mol_dft)
    mf_dft.xc = xc_code
    E = mf_dft.kernel()
    print(f"  {xc_name:15s}/STO-3G: E = {E:.6f} Hartree")

# ====================================================================
# 3. H2 molecule: HF/STO-3G, single point at R=1.4 bohr
# ====================================================================
print("\n--- 3. H2 HF/STO-3G at R=1.4 bohr ---")
R = 1.4
mol_h2 = gto.M(atom=f'H 0 0 {-R/2}; H 0 0 {R/2}', basis='sto-3g',
               unit='bohr', verbose=0)
mf_h2 = scf.RHF(mol_h2)
E_h2_hf = mf_h2.kernel()
S_h2 = mf_h2.get_ovlp()
H_h2 = mf_h2.get_hcore()
eri_h2 = mol_h2.intor('int2e')
print(f"  E_HF = {E_h2_hf:.6f} Hartree")
print(f"  Our code: E_HF = -1.116714 Hartree")
print(f"  S[0,1] = {S_h2[0,1]:.6f}  (our: 0.659318)")
print(f"  H_core = [{H_h2[0,0]:.6f}, {H_h2[0,1]:.6f}]")
print(f"  (11|11) = {eri_h2[0,0,0,0]:.6f}  (our: 0.774606)")
print(f"  (11|22) = {eri_h2[0,0,1,1]:.6f}  (our: 0.569676)")
print(f"  (12|12) = {eri_h2[0,1,0,1]:.6f}  (our: 0.297029)")

# ====================================================================
# 4. H2 molecule: DFT/LDA at R=1.4 bohr
# ====================================================================
print("\n--- 4. H2 DFT/LDA/STO-3G at R=1.4 bohr ---")
mol_h2_lda = gto.M(atom=f'H 0 0 {-R/2}; H 0 0 {R/2}', basis='sto-3g',
                    unit='bohr', verbose=0)
mf_lda = dft.RKS(mol_h2_lda)
mf_lda.xc = 'lda,vwn'
E_h2_lda = mf_lda.kernel()
print(f"  E_LDA = {E_h2_lda:.6f} Hartree")
print(f"  Our code: E_LDA = -1.073105 Hartree")

# ====================================================================
# 5. H2 HF/STO-3G potential energy curve
# ====================================================================
print("\n--- 5. H2 HF/STO-3G Potential Energy Curve ---")
Rs = np.linspace(0.5, 5.0, 50)
E_hf_curve = np.zeros(len(Rs))
E_lda_curve = np.zeros(len(Rs))
for idx, R_val in enumerate(Rs):
    mol_r = gto.M(atom=f'H 0 0 {-R_val/2}; H 0 0 {R_val/2}',
                  basis='sto-3g', unit='bohr', verbose=0)
    mf_r = scf.RHF(mol_r)
    E_hf_curve[idx] = mf_r.kernel()

    mf_lda_r = dft.RKS(mol_r)
    mf_lda_r.xc = 'lda,vwn'
    E_lda_curve[idx] = mf_lda_r.kernel()

i_hf = np.argmin(E_hf_curve)
i_lda = np.argmin(E_lda_curve)
print(f"  HF  (PySCF): R_eq = {Rs[i_hf]:.3f} bohr, E_min = {E_hf_curve[i_hf]:.6f}")
print(f"  HF  (ours):  R_eq = 1.327 bohr, E_min = -1.117396")
print(f"  LDA (PySCF): R_eq = {Rs[i_lda]:.3f} bohr, E_min = {E_lda_curve[i_lda]:.6f}")
print(f"  LDA (ours):  R_eq = 1.418 bohr, E_min = -1.073004")
print(f"  Dissociation limit: HF(R=5)={E_hf_curve[-1]:.6f}, LDA(R=5)={E_lda_curve[-1]:.6f}")

D_e_hf = abs(E_hf_curve[i_hf] - E_hf_curve[-1])
D_e_lda = abs(E_lda_curve[i_lda] - E_lda_curve[-1])
print(f"  D_e HF:  PySCF={D_e_hf:.6f} Ha ({D_e_hf*27.2114:.3f} eV), ours=0.117 Ha (3.195 eV)")
print(f"  D_e LDA: PySCF={D_e_lda:.6f} Ha ({D_e_lda*27.2114:.3f} eV), ours=0.073 Ha (1.987 eV)")

# ====================================================================
# 6. H2 DFT with PBE and B3LYP (reference values for ch15)
# ====================================================================
print("\n--- 6. H2 DFT/PBE and B3LYP/STO-3G at R=1.4 bohr ---")
for xc_name, xc_code in [('PBE', 'pbe,pbe'), ('B3LYP', 'b3lyp')]:
    mol_xc = gto.M(atom=f'H 0 0 {-R/2}; H 0 0 {R/2}', basis='sto-3g',
                    unit='bohr', verbose=0)
    mf_xc = dft.RKS(mol_xc)
    mf_xc.xc = xc_code
    E = mf_xc.kernel()
    print(f"  {xc_name:6s}/STO-3G: E = {E:.6f} Hartree")

# ====================================================================
# 7. Validation Summary
# ====================================================================
print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

delta_hf_r14 = abs(-1.116714 - E_h2_hf)
delta_lda_r14 = abs(-1.073105 - E_h2_lda)
delta_hf_Req = abs(1.327 - Rs[i_hf])
delta_lda_Req = abs(1.418 - Rs[i_lda])

print(f"  H2 HF/STO-3G at R=1.4 bohr:")
print(f"    Our E = -1.116714, PySCF E = {E_h2_hf:.6f}, diff = {delta_hf_r14:.6f} Ha ({delta_hf_r14*27.2114:.4f} eV)")
if delta_hf_r14 < 0.001:
    print(f"    PASS: difference < 1 mHa")
else:
    print(f"    WARN: difference = {delta_hf_r14*1000:.2f} mHa")

print(f"  H2 HF/STO-3G equilibrium:")
print(f"    Our R_eq = 1.327, PySCF R_eq = {Rs[i_hf]:.3f}, diff = {delta_hf_Req:.3f} bohr")

print(f"  H2 LDA/STO-3G at R=1.4 bohr:")
print(f"    Our E = -1.073105, PySCF E = {E_h2_lda:.6f}, diff = {delta_lda_r14:.6f} Ha ({delta_lda_r14*27.2114:.4f} eV)")
if delta_lda_r14 < 0.01:
    print(f"    PASS: difference < 10 mHa (grid integration tolerance)")
else:
    print(f"    WARN: difference = {delta_lda_r14*1000:.2f} mHa (grid integration may differ)")

# Compare integrals directly
print(f"\n  Integral comparison (H2, R=1.4 bohr, STO-3G):")
print(f"    {'Quantity':<15s} {'Our code':>12s} {'PySCF':>12s} {'Diff':>12s}")
print(f"    {'-'*51}")
print(f"    {'S[0,1]':<15s} {'0.659318':>12s} {S_h2[0,1]:>12.6f} {abs(0.659318-S_h2[0,1]):>12.8f}")
print(f"    {'H_core[0,0]':<15s} {'-1.120409':>12s} {H_h2[0,0]:>12.6f} {abs(-1.120409-H_h2[0,0]):>12.8f}")
print(f"    {'(11|11)':<15s} {'0.774606':>12s} {eri_h2[0,0,0,0]:>12.6f} {abs(0.774606-eri_h2[0,0,0,0]):>12.8f}")
print(f"    {'(11|22)':<15s} {'0.569676':>12s} {eri_h2[0,0,1,1]:>12.6f} {abs(0.569676-eri_h2[0,0,1,1]):>12.8f}")
print(f"    {'(12|12)':<15s} {'0.297029':>12s} {eri_h2[0,1,0,1]:>12.6f} {abs(0.297029-eri_h2[0,1,0,1]):>12.8f}")

print("\nDone.")
