# 2. Conservation of Information

## Local Conservation Law

Information inside a region can change due to:

1. flow across boundaries
2. internal creation or destruction

The general conservation equation is:

\[
\frac{\partial s}{\partial t} + \nabla \cdot J = S
\]

Where:

| Symbol | Meaning |
|------|------|
| s | information density |
| J | information flux |
| S | source/sink term |

---

## Physical Interpretation

Term breakdown:

\[
\frac{\partial s}{\partial t}
\]

local change of information density

\[
\nabla \cdot J
\]

net outward flow of information

\[
S
\]

creation or destruction of information

---

## Global Form

Integrating over a volume \(V\):

\[
\frac{d}{dt}\int_V s\,dV = -\oint J \cdot dA + \int_V S\,dV
\]

This expresses global conservation.

---

## Importance

This equation is the **fundamental starting point** of the theory.

Every dynamical equation must be consistent with this conservation law.
