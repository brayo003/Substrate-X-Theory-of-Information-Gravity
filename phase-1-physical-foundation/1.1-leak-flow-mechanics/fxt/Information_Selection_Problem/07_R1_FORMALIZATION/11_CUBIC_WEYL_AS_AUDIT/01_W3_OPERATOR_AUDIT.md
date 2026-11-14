# 01_W3_OPERATOR_AUDIT
## Is W₃ an Independent Operator in the 4D Gravitational Basis?

**Date:** August 2026

---

## The Operator in Question

The cubic Weyl invariant in four-dimensional Riemannian/Lorentzian spacetime is:

  W₃ = C_{αβ}^{\ \ γδ} C_{γδ}^{\ \ εζ} C_{εζ}^{\ \ αβ}

This is the Chern-Simons-like trace of three Weyl tensors contracted cyclically. In 4D there are two independent cubic Weyl scalars:

  I₁ = C_{αβγδ} C^{αβ}_{\ \ εζ} C^{γδεζ}   (the "E-type" or "P-type" cubic)
  I₂ = C_{αβγδ} C^{α\ γ}_{\ ε\ ζ} C^{β\ δ\ εζ}   (the "B-type" cubic)

In the physics literature these are often written using the electric-magnetic decomposition of the Weyl tensor:

  E_{ij} = C_{i0j0}   (electric Weyl)
  B_{ij} = (1/2)ε_{ikl}C^{kl}_{\ \ j0}   (magnetic Weyl)

  I₁ ~ Tr(E³) − 3 Tr(E B²)   (parity-even cubic)
  I₂ ~ Tr(B³) − 3 Tr(B E²)   (parity-odd cubic)

In 4D, I₂ is parity-odd (it changes sign under orientation reversal). In a parity-invariant gravitational theory, I₂ cannot appear alone in the effective action. Therefore the relevant independent parity-even cubic Weyl operator is I₁ (or an equivalent linear combination).

---

## Independence in the 4D Basis

The gravitational effective action at each order in derivatives contains independent diffeomorphism-invariant scalar operators. At order ∂⁶ (six derivatives, or "order-6 in curvature" counting each Riemann as two derivatives):

**Complete basis of independent 6th-order operators in 4D:**

Using the Gauss-Bonnet identity and Bianchi identities, one can reduce the independent operators. The standard basis includes:

At order R³ (Ricci-scalar cubic):
  R³, R R_{μν}R^{μν}, R_{μν}R^{νρ}R_{ρ}^{\ μ}

At order Riemann³ (schematic):
  C_{αβγδ}C^{αβ}_{\ \ εζ}C^{γδεζ},   R_{αβ}R^{αβγδ}R_{γδ},   R^{μν}R^{ρσ}C_{μρνσ}, ...

In 4D the full basis of independent 6th-order scalars built from Riemann and its covariant derivatives (at zero derivative order) has 17 independent terms (Boulware-Deser 1985, Fulling et al. 1992).

**Is W₃ = C_{αβγδ}C^{αβ}_{εζ}C^{γδεζ} independent?**

YES — it cannot be written as a linear combination of other 6th-order operators. The Boulware-Deser basis includes it explicitly as an independent element. It is not removable by integration by parts or by field redefinitions (unlike some ∂²R operators).

**Key point for Kasner:** Operators involving R or R_{μν} vanish on vacuum Kasner (Ricci-flat). Of the 17 basis elements at 6th order, only those built purely from the Weyl tensor are potentially nonzero on Kasner. These are exactly the cubic-Weyl operators I₁ and (for the parity-preserving case) I₁.

---

## Operator Counting on Kasner

On vacuum Kasner (R_{μν} = 0, R = 0):

- All operators containing R or R_{μν} as factors: VANISH
- All operators containing covariant derivatives of R: VANISH (since ∇R = ∇R_{μν} = 0 for Kasner vacuum by contracted Bianchi)
- Operators built purely from C_{αβγδ}: NONZERO

The operators that remain nonzero on Kasner at 6th order are:
- I₁ = C_{αβγδ}C^{αβ}_{\ εζ}C^{γδεζ} (the parity-even cubic Weyl)
- I₂ = parity-odd cubic (relevant only if parity is broken)

Therefore **W₃ = I₁ is the unique relevant 6th-order scalar that is nonzero on Kasner and could potentially contribute a nonzero variation δW₃/δg on Kasner.**

---

## Conclusion

W₃ is a genuine independent operator in the 4D gravitational basis. It is not reducible to lower-order operators or to Ricci-dependent terms. On vacuum Kasner, it is nonzero. It is the first (and lowest-order) Weyl-polynomial operator that could potentially have nonzero variation on Kasner. This is why the C³/w₃* calculation is the most promising remaining route.

---

*Document status: W₃ OPERATOR AUDIT COMPLETE*
*W₃ is independent in the 4D basis. It is nonzero on Kasner. The variation δW₃/δg|_{Kasner} is the object to compute.*
*Date: August 2026*
