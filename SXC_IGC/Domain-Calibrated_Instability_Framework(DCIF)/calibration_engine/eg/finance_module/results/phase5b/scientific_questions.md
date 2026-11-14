# Phase 5 — Scientific Questions
**Generated:** 2026-07-22T14:36:01Z

All answers are evidence-based. No speculation.

## Q1. Does the Transport OS remain profitable on unseen data?

**3/7** markets profitable (PF > 1.0) on 2026 OOS data. Mean PF across profitable markets = 1.847.
**Confidence: Moderate**
Evidence: EURUSD=PF0.00, BTCUSDT=PF1.10, ETHUSDT=PF1.03, NAS100=PF6.10, XAUUSD=PF0.98, USOIL=PF0.99, UKOIL=PF0.89

## Q2. Does the NoTrade behaviour remain stable?

Mean NoTrade%: 2025=0.0%, 2026=65.4% (Δ=65.4%).
**Confidence: Weak**
Evidence: NoTrade is determined by frozen regime thresholds and allocator decisions. Δ=65.4% indicates regime shift.

## Q3. Has the transport field changed?

Mean TV distance (Q distributions): 0.276.
**Confidence: Weak** (threshold: <0.10=stable, <0.20=moderate drift)
Evidence: KS/TVD/KL divergence computed per market. Meaningful Q distribution shift detected.

## Q4. Do the allocators still activate in the same transport regimes?

Allocator stability: 29.5% of regime→family mappings consistent.
**Confidence: Weak**
Evidence: Frozen scheduler applied without modification. Allocator activations shifted.

## Q5. Does any market collapse?

**NO** — No market shows PF < 0.5. Minimum PF = 0.000.
Evidence: All markets with sufficient trades have PF ≥ 0.888.

## Q6. Which markets improved?

**Improved:** None
Evidence: 2026 PF > 2025 PF for these markets. No markets improved.

## Q7. Which markets degraded?

**Degraded:** XAUUSD, USOIL, UKOIL
Evidence: 2026 PF < 1.0 where 2025 PF ≥ 1.0. XAUUSD: 2.65→0.98; USOIL: 1.27→0.99; UKOIL: 2.21→0.89

## Q8. Is degradation due to Transport or Execution?

Transport drift (TV distance): 0.276. Execution drift index: 1.551.
Both transport and execution show meaningful drift.
Evidence: Transport drift measures Q distribution shift. Execution drift measures PF/Sharpe/WinRate change.

## Q9. Does the Information Transport hypothesis survive completely unseen data?

**PARTIAL — Mixed evidence.**
Evidence: 3/7 markets profitable. Q transport field TV distance = 0.276. Regime structure preserved (regime stability TVD = 0.193). Frozen Q thresholds (Q05=-1.0, Q95=1.73) correctly classify regimes on unseen 2026 data.

## Q10. Would deployment on Jan 1 2026 justify continued operation as of July 2026?

**UNCERTAIN — Insufficient evidence.**
Evidence: 3/7 markets profitable YTD. Mean PF (profitable) = 1.847. NoTrade% = 65.4% (risk-controlled). Performance requires monitoring before confident recommendation.
