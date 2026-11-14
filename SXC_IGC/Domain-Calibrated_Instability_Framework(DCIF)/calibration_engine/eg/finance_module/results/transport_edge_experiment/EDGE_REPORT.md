# Transport Edge Experiment — Evidence Report
Generated: 2026-10-11 12:08 UTC
IS: 2023-01–2024-06  |  WF1: 2024-07–2024-12  |  WF2: 2025-01–2025-10
Cost: 5.0pip RT

## Success criteria (pre-defined)
WF combined: PF>1.10, exp>+2pip, CI_lo>-3pip, PF_2x>1.0, N>=50, min_fold_PF>=0.60

## IS Performance
           strategy period  n_trades  win_rate  profit_factor  expectancy_pips  total_net_pips  max_drawdown_pips  pf_2x_cost  avg_win_pip  avg_loss_pip  ci_lo  ci_hi
  A_Transport_Trend     IS        27     0.074          0.070            -5.32          -143.5              127.6       0.013          5.4          -6.2  -7.24  -3.45
   B_Wide_EMA_Cross     IS      2601     0.308          0.366            -5.00        -12996.6            12986.5       0.142          9.4         -11.4  -5.46  -4.54
    C_ST_Divergence     IS      1593     0.244          0.210            -5.40         -8598.9             8592.5       0.051          5.9          -9.0  -5.77  -5.00
D_Vol_Breakout_Base     IS      3373     0.335          0.352            -4.97        -16747.9            16776.0       0.118          8.0         -11.5  -5.32  -4.62

## WF1 Performance
           strategy period  n_trades  win_rate  profit_factor  expectancy_pips  total_net_pips  max_drawdown_pips  pf_2x_cost  avg_win_pip  avg_loss_pip  ci_lo  ci_hi
  A_Transport_Trend    WF1         4     0.000          0.000            -6.06           -24.3               18.1       0.000          NaN          -6.1    NaN    NaN
   B_Wide_EMA_Cross    WF1       889     0.303          0.349            -4.91         -4362.1             4400.2       0.130          8.7         -10.8  -5.68  -4.14
    C_ST_Divergence    WF1       574     0.233          0.225            -5.00         -2870.0             2863.6       0.056          6.2          -8.4  -5.60  -4.38
D_Vol_Breakout_Base    WF1      1096     0.287          0.291            -5.49         -6020.4             6047.8       0.095          7.8         -10.9  -6.07  -4.88

## WF2 Performance
           strategy period  n_trades  win_rate  profit_factor  expectancy_pips  total_net_pips  max_drawdown_pips  pf_2x_cost  avg_win_pip  avg_loss_pip  ci_lo  ci_hi
  A_Transport_Trend    WF2         8     0.125          0.277            -3.42           -27.4               28.7       0.076         10.5          -5.4  -6.03   0.96
   B_Wide_EMA_Cross    WF2      1415     0.360          0.490            -4.46         -6311.4             6331.2       0.222         11.9         -13.7  -5.26  -3.67
    C_ST_Divergence    WF2      1059     0.308          0.415            -4.35         -4603.9             4598.3       0.159         10.0         -10.7  -5.07  -3.65
D_Vol_Breakout_Base    WF2      1855     0.366          0.456            -4.93         -9152.4             9190.6       0.199         11.3         -14.3  -5.57  -4.30

## WF Combined Decision
  A_Transport_Trend: FAIL: PF=0.169<1.10; exp=-4.30<+2pip; CI_lo=-6.3<-3pip; PF_2x=0.047<1.0; N=12<50; min_fold_PF=0.000<0.60
  B_Wide_EMA_Cross: FAIL: PF=0.440<1.10; exp=-4.63<+2pip; CI_lo=-5.2<-3pip; PF_2x=0.188<1.0; min_fold_PF=0.349<0.60
  C_ST_Divergence: FAIL: PF=0.355<1.10; exp=-4.58<+2pip; CI_lo=-5.1<-3pip; PF_2x=0.124<1.0; min_fold_PF=0.225<0.60
  D_Vol_Breakout_Base: FAIL: PF=0.400<1.10; exp=-5.14<+2pip; CI_lo=-5.6<-3pip; PF_2x=0.162<1.0; min_fold_PF=0.291<0.60

## What remains to investigate
- Higher ATR/cost ratio instrument (Gold, GBP/USD, NAS100 at 5-min)
- Whether transport regime signal improves entry on daily bars (larger ATR)
- C_ST_Divergence: conceptually sound but threshold may need IS recalibration