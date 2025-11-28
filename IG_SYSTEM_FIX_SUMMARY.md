# INFORMATION GRAVITY SYSTEM FIX SUMMARY

## PROBLEM IDENTIFIED
- **IG scores range**: 0.014 to 0.350 (very low)
- **Current thresholds**: EXPAND=0.9, CONTRACT=0.8 (too high)
- **Result**: All signals are "CONTRACT" regardless of input
- **Thresholds inverted**: EXPAND > CONTRACT (illogical)

## SOLUTION
Update the thresholds in `applications/universal_risk_indicator.py`:

```python
# CURRENT (BROKEN)
EXPAND_THRESHOLD = 0.9    # Too high - never reached
CONTRACT_THRESHOLD = 0.8  # Too high - illogical ordering

# RECOMMENDED (FIXED)
EXPAND_THRESHOLD = 0.117   # IG > 0.117 -> EXECUTE/EXPAND
CONTRACT_THRESHOLD = 0.023 # IG < 0.023 -> CONTRACT/STAND ASIDE
# Between 0.023 and 0.117 -> CAUTION/HOLD
clear
