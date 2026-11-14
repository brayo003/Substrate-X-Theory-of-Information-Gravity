# SXC-IGC Summary Dashboard — Validation V2

Dataset: 8,387 bars  |  2023-01-01 → 2025-05-29

## Key Numbers

| Metric | Value |
|---|---|
| Coherent fraction | 16.2% |
| P(stay coherent) | 0.212 |
| P(stay incoherent) | 0.849 |
| Mean coherent run | 1.3 bars |
| Vol expansion at transition | 1.217x |
| Vol expansion p-value | 0.0000 |

## Capability Ratings

- **strategy_selection**: Weak
- **position_sizing**: None
- **risk_management**: Moderate
- **execution**: Moderate
- **volatility_forecasting**: Strong
- **trade_filtering**: None
- **portfolio_allocation**: None

## Final Verdict

**A: Q is only another technical indicator.**

## Output Files

| File | Contents |
|---|---|
| transport_regime_validation_v2.md | Full 10-phase report |
| market_state_report.md | Is Q a market-state variable? |
| regime_transition_events.csv | Every Q regime episode |
| volatility_event_profiles.csv | Vol profile around Q transitions |
| lead_lag_comparison.csv | Q vs ADX/ATR/HV lead-lag |
| strategy_regime_matrix.csv | 4 strategies × 2 regimes |
| risk_management_matrix.csv | Stop/target results by Q bucket |
| execution_matrix.csv | Spread/IAE by regime |
| capability_table.csv | Ranked practical capabilities |
| plots/ | All V2 plots |