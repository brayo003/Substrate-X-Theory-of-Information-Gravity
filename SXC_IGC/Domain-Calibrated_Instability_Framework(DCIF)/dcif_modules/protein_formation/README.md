# Protein Formation Module (V12 Omega)

This module implements the **Domain-Calibrated Instability Framework (DCIF)** on molecular substrates. It translates raw atomic coordinates (PDB) into **Information Gravity** signatures to detect structural maturity and "Black Hole" collapse states.

## Core Equation
The engine tracks the tension functional:
$$T = \alpha|\nabla\rho| + \beta E - \gamma F$$

In this module, $\beta E$ (Energy) is represented by the local atomic packing density, while $\gamma F$ (Resilience) represents the protein's ability to dissipate structural stress.

## The Experiment
We audited three distinct biological states to test the **Scale-Invariance** of the V12 Engine:

1.  **Ubiquitin (1UBQ):** The "Control." A hyper-stable, functional protein.
2.  **Prion (1QLX):** The "Threat." A metastable protein prone to dynamic fracture.
3.  **Amyloid-Beta (2MXU):** The "Collapse." A saturated, crystalline aggregate (Information Black Hole).

## Results & Phase Map

| Target | Peak $T_{sys}$ | Index ($I$) | V12 Status | Substrate State |
| :--- | :--- | :--- | :--- | :--- |
| **Ubiquitin** | 22.48 | 1.2250 | `OPTIMAL` | Functional Flow |
| **Prion** | 26.03 | 1.3882 | `FRACTURE` | Dynamic Instability |
| **Amyloid** | 307.16 | 1.1964 | `COLLAPSE` | Crystalline Saturation |

### Findings: The Amyloid Paradox
While the **Instability Index** ($Peak/Avg$) is low for Amyloids, the **Absolute Tension** is $>1000\%$ higher than functional proteins. This confirms that "Stability" in Substrate X can be lethal; the Amyloid state is an **Information Black Hole** where gravity is so high that the substrate becomes static (Dead).



## Files
* `v12_omega_final.py`: The core audit engine with Saturation Override.
* `ubiquitin.pdb` / `prion.pdb` / `amyloid.pdb`: Raw structural data.

---
*Part of the Substrate X Theory of Information Gravity*
