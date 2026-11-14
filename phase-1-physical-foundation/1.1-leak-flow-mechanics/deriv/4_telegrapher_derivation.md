# 4. Telegrapher Equation Derivation

## Motivation

Pure diffusion equations propagate signals infinitely fast.

Physical systems usually exhibit finite propagation speed.

To correct this we introduce a **flux relaxation time**.

---

## Maxwell–Cattaneo Relation

Instead of instant flux response:

\[
J = -D\nabla s + s v_{sub} + \chi s u
\]

we introduce:

\[
\tau \frac{\partial J}{\partial t} + J =
- D\nabla s + s v_{sub} + \chi s u
\]

Where:

τ = flux relaxation time.

---

## Combine with Conservation Law

Recall:

\[
\frac{\partial s}{\partial t} + \nabla\cdot J = S
\]

Taking divergence of the relaxation equation and substituting gives:

\[
\tau \frac{\partial^2 s}{\partial t^2}
+
\frac{\partial s}{\partial t}
=
D\nabla^2 s
-
\nabla\cdot(s v_{sub})
-
\nabla\cdot(\chi s u)
+
S
\]

---

## Identification of Diffusivity

Let

\[
D = c^2 \tau
\]

Then

\[
\tau \partial_{tt}s + \partial_t s =
c^2\tau\nabla^2 s
-
\nabla\cdot(s v_{sub})
-
\nabla\cdot(\chi s u)
+
S
\]

This is the **telegrapher transport equation** governing information density.
