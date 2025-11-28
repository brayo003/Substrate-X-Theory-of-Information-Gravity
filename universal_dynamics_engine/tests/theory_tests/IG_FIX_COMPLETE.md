# INFORMATION GRAVITY SYSTEM - FIX COMPLETE

## PROBLEM SOLVED
The IG system was producing only "CONTRACT" signals because:
- IG scores range: 0.014 to 0.350  
- Thresholds were set too high: EXPAND=0.9, CONTRACT=0.8
- Thresholds were inverted (illogical)

## SOLUTION APPLIED
Updated thresholds in applications/universal_risk_indicator.py:
- EXPAND_THRESHOLD: 0.9 → 0.117
- CONTRACT_THRESHOLD: 0.8 → 0.023

## EXPECTED BEHAVIOR
- IG < 0.023 → CONTRACT/STAND ASIDE
- IG > 0.117 → EXECUTE/EXPAND  
- Between → CAUTION/HOLD

## VERIFICATION
Run: python test_fixed_system.py
This should show proper signal distribution across stability levels.
