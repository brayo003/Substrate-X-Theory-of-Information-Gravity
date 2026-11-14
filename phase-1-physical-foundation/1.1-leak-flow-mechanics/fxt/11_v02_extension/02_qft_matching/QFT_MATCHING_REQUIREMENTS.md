# Workstream 2 — QFT/Matching Route

This is a requirements document, not a claimed QFT derivation.

To say that a microscopic completion fixes `g`, v02 must provide all of:

1. A field variable with physical units and a specified action.
2. A symmetry group and transformation rule for that field and the qubit.
3. An interaction operator whose low-energy limit is `J sigma_z`.
4. A regulator and renormalization prescription.
5. A matching calculation at a stated scale that gives `g(mu)`.
6. A running/scale-dependence prediction or a reason it is absent.
7. A comparison with the standard effective-field-theory operator basis.

Without these items, phrases such as “QFT origin” or “renormalization fixes the
coupling” are research aspirations, not derivations.

## Falsifier

A proposed completion fails if its low-energy matching leaves an arbitrary
finite coefficient multiplying `J sigma_z`, because that coefficient is simply
the original free `g` in new notation.
