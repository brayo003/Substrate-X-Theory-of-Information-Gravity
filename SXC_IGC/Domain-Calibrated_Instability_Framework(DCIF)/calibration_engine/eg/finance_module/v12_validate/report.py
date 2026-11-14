"""
report.py — Generate the final technical validation report as plain text.
"""

from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd


def _stars(p) -> str:
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return ''
    if p < 0.001:
        return '***'
    if p < 0.01:
        return '**'
    if p < 0.05:
        return '*'
    return 'ns'


def write_report(
    out_dir: Path,
    data_summary: dict,
    v12: pd.DataFrame,
    transitions: pd.DataFrame,
    compare_df: pd.DataFrame,
    pred_df: pd.DataFrame,
    perm_results: list,
    stab_year: pd.DataFrame,
    stab_sess: pd.DataFrame,
    fwd_df: pd.DataFrame,
    xcorr: pd.Series,
):
    report_lines = []
    w = report_lines.append

    def section(title):
        w('')
        w('=' * 72)
        w(title)
        w('=' * 72)

    def sub(title):
        w('')
        w(title)
        w('-' * len(title))

    w('V12 / SXCOmega — EMPIRICAL VALIDATION REPORT')
    w(f'Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}')

    # ------------------------------------------------------------------
    # 1. Dataset summary
    # ------------------------------------------------------------------
    section('1. DATASET SUMMARY')
    for k, v in data_summary.items():
        w(f'  {k:<28} {v}')

    # ------------------------------------------------------------------
    # 2. V12 state history summary
    # ------------------------------------------------------------------
    section('2. V12 CONTINUOUS STATE HISTORY')
    total_bars   = len(v12)
    fw_bars      = (v12['phase'] == 'FIREWALL').sum()
    nm_bars      = (v12['phase'] == 'NOMINAL').sum()
    fw_pct       = fw_bars / total_bars * 100
    nm_pct       = nm_bars / total_bars * 100
    n_fw_eps     = len(transitions[transitions['phase'] == 'FIREWALL'])
    n_nm_eps     = len(transitions[transitions['phase'] == 'NOMINAL'])
    fw_dur       = transitions[transitions['phase'] == 'FIREWALL']['duration_min']
    nm_dur       = transitions[transitions['phase'] == 'NOMINAL']['duration_min']

    w(f'  Total bars analysed    : {total_bars:,}')
    w(f'  FIREWALL bars          : {fw_bars:,}  ({fw_pct:.1f} %)')
    w(f'  NOMINAL bars           : {nm_bars:,}  ({nm_pct:.1f} %)')
    w(f'  FIREWALL episodes      : {n_fw_eps:,}')
    w(f'  NOMINAL  episodes      : {n_nm_eps:,}')
    if not fw_dur.empty:
        w(f'  FIREWALL dur  median   : {fw_dur.median():.0f} min')
        w(f'  FIREWALL dur  p90      : {fw_dur.quantile(0.90):.0f} min')
        w(f'  FIREWALL dur  max      : {fw_dur.max():.0f} min')
    if not nm_dur.empty:
        w(f'  NOMINAL  dur  median   : {nm_dur.median():.0f} min')
        w(f'  NOMINAL  dur  p90      : {nm_dur.quantile(0.90):.0f} min')

    w('')
    w('  T_sys descriptive statistics:')
    for stat, val in v12['T_sys'].describe().items():
        w(f'    {stat:<12} {val:.4f}')

    # ------------------------------------------------------------------
    # 3. Contemporaneous validation
    # ------------------------------------------------------------------
    section('3. CONTEMPORANEOUS VALIDATION  (FIREWALL vs NOMINAL)')
    sub('Mann-Whitney U tests with rank-biserial effect size')
    w(f'  {"Label":<22} {"FW mean":>9} {"NM mean":>9} {"r":>7} {"p":>10} {"sig":>4}')
    w('  ' + '-' * 65)
    for _, row in compare_df.sort_values('rank_biserial_r', ascending=False).iterrows():
        sig = _stars(row.get('p_value'))
        w(f'  {row["label"]:<22} '
          f'{row["FIREWALL_mean"]:>9.4f} '
          f'{row["NOMINAL_mean"]:>9.4f} '
          f'{row["rank_biserial_r"]:>7.3f} '
          f'{row["p_value"]:>10.2e} '
          f'{sig:>4}')
    w('')
    w('  Significance codes: *** p<0.001  ** p<0.01  * p<0.05  ns = not significant')
    w('  Positive r → FIREWALL has higher values; negative r → NOMINAL higher.')

    # ------------------------------------------------------------------
    # 4. Predictive validation
    # ------------------------------------------------------------------
    section('4. PREDICTIVE VALIDATION  (Spearman ρ: T_sys vs future labels)')
    rho_cols = [c for c in pred_df.columns if c.startswith('rho_k')]
    p_cols   = [c for c in pred_df.columns if c.startswith('p_k')]
    horizons = [c.replace('rho_k', '') for c in rho_cols]

    header = f'  {"Label":<22}' + ''.join(f'  k={h:>4}' for h in horizons)
    w(header)
    w('  ' + '-' * len(header))
    for _, row in pred_df.iterrows():
        line = f'  {row["label"]:<22}'
        for rho_c, p_c in zip(rho_cols, p_cols):
            rho = row[rho_c]
            p   = row[p_c]
            sig = _stars(p)
            cell = f'{rho:+.3f}{sig}' if not np.isnan(rho) else '     —  '
            line += f'  {cell:>8}'
        w(line)
    w('')
    w('  * = p<0.05 against T_sys(t) predicting label(t+k)')

    # Lead/lag peak
    sub('Lead/lag cross-correlation peak (T_sys vs realized_vol)')
    if xcorr is not None and not xcorr.empty:
        peak_lag = xcorr.abs().idxmax()
        peak_val = xcorr.iloc[xcorr.index.get_loc(peak_lag)]
        w(f'  Peak correlation: r={peak_val:.3f} at lag={peak_lag} bars ({peak_lag*5} min)')
        w(f'  Positive lag means T_sys leads realized volatility.')

    # ------------------------------------------------------------------
    # 5. Forward window analysis
    # ------------------------------------------------------------------
    section('5. POST-FIREWALL FORWARD WINDOW  (ratio to NOMINAL baseline)')
    if fwd_df is not None and not fwd_df.empty:
        ratio_cols = [c for c in fwd_df.columns if c.endswith('_vs_nominal')]
        horizons_h = sorted(fwd_df['horizon_min'].unique())
        header2 = f'  {"Horizon":<12}' + ''.join(f'  {c.replace("mean_","").replace("_vs_nominal",""):>12}' for c in ratio_cols)
        w(header2)
        w('  ' + '-' * len(header2))
        for h in horizons_h:
            sub_h = fwd_df[fwd_df['horizon_min'] == h]
            line  = f'  {h:>4} min   '
            for col in ratio_cols:
                val = sub_h[col].mean()
                line += f'  {val:>12.3f}'
            w(line)
        w('')
        w('  Values > 1.0 indicate post-FIREWALL conditions exceed NOMINAL baseline.')

    # ------------------------------------------------------------------
    # 6. Permutation tests
    # ------------------------------------------------------------------
    section('6. PERMUTATION TESTS  (empirical null distribution)')
    w(f'  {"Label":<22} {"Observed r":>12} {"Null p95":>10} {"p_perm":>10} {"sig":>4}')
    w('  ' + '-' * 62)
    for res in perm_results:
        sig = _stars(res.get('p_permutation'))
        w(f'  {res["label"]:<22} '
          f'{res["observed_r"]:>12.4f} '
          f'{res.get("null_r_p95", float("nan")):>10.4f} '
          f'{res["p_permutation"]:>10.4f} '
          f'{sig:>4}')

    # ------------------------------------------------------------------
    # 7. Stability
    # ------------------------------------------------------------------
    section('7. STABILITY ANALYSIS')
    sub('Rank-biserial r by year (realized_vol)')
    if not stab_year.empty:
        rv_yr = stab_year[stab_year['label'] == 'realized_vol']
        if not rv_yr.empty:
            for _, row in rv_yr.iterrows():
                sig = _stars(row['p_value'])
                w(f'  {row["year"]}  r={row["rank_biserial_r"]:+.3f}  '
                  f'p={row["p_value"]:.3e}  {sig}  '
                  f'(n_fw={row["n_fw"]}, n_nm={row["n_nm"]})')

    sub('Rank-biserial r by trading session (realized_vol)')
    if not stab_sess.empty:
        rv_sess = stab_sess[stab_sess['label'] == 'realized_vol']
        if not rv_sess.empty:
            for _, row in rv_sess.iterrows():
                sig = _stars(row['p_value'])
                w(f'  {str(row["session"]):<8}  r={row["rank_biserial_r"]:+.3f}  '
                  f'p={row["p_value"]:.3e}  {sig}')

    # ------------------------------------------------------------------
    # 8. Failure cases
    # ------------------------------------------------------------------
    section('8. FAILURE CASES AND LIMITATIONS')
    # Find labels where FIREWALL is NOT significantly different from NOMINAL
    if not compare_df.empty:
        non_sig = compare_df[~compare_df['significant']]
        if not non_sig.empty:
            w('  Labels where FIREWALL ≠ NOMINAL is NOT significant (p >= 0.05):')
            for _, row in non_sig.iterrows():
                w(f'    {row["label"]}  (p={row["p_value"]:.3f})')
        else:
            w('  All tested labels are significant.')

    w('')
    w('  Known limitations:')
    w('  - V12 parameters (β=3.5, γ=0.8) are fixed; no per-instrument calibration.')
    w('  - Composite signal is unweighted mean of 6 normalised signals.')
    w('  - Composite is scaled ×100 for the excitation_flux piecewise function.')
    w('  - γ decays over time and is not reset between analysis windows.')
    w('  - 2025 CSV data has limited coverage; data imbalance possible.')
    w('  - Spread signal is itself a V12 input, so spread comparison is partially circular.')

    # ------------------------------------------------------------------
    # 9. Final conclusion
    # ------------------------------------------------------------------
    section('9. FINAL CONCLUSION')

    # Q1: meaningful regimes
    key_labels = ['realized_vol', 'atr', 'spread_abs', 'adx']
    sig_count = 0
    pos_count = 0
    if not compare_df.empty:
        sub_df = compare_df[compare_df['label'].isin(key_labels)]
        sig_count = sub_df['significant'].sum()
        pos_count = (sub_df['rank_biserial_r'] > 0).sum()

    w('  Q1. Does V12 consistently identify meaningful market regimes?')
    if sig_count >= 3:
        w(f'  ANSWER: YES.  {sig_count}/{len(key_labels)} key market labels differ')
        w('    significantly between FIREWALL and NOMINAL (p<0.05).')
    elif sig_count >= 1:
        w(f'  ANSWER: PARTIAL.  {sig_count}/{len(key_labels)} key labels differ')
        w('    significantly; effect is present but not universal.')
    else:
        w('  ANSWER: NO.  No key market label differs significantly.')

    w('')
    w('  Q2. Does FIREWALL correspond to objectively unstable market conditions?')
    rv_row = compare_df[compare_df['label'] == 'realized_vol'] if not compare_df.empty else pd.DataFrame()
    if not rv_row.empty:
        r_val = rv_row.iloc[0]['rank_biserial_r']
        p_val = rv_row.iloc[0]['p_value']
        sig   = _stars(p_val)
        if r_val > 0.1 and p_val < 0.05:
            w(f'  ANSWER: YES.  FIREWALL bars have significantly higher realized')
            w(f'    volatility (r={r_val:.3f}, {sig}).')
        elif r_val > 0 and p_val < 0.05:
            w(f'  ANSWER: WEAKLY YES.  Small positive effect on realized vol (r={r_val:.3f}, {sig}).')
        else:
            w(f'  ANSWER: UNCERTAIN.  Realized vol difference not significant.')
    else:
        w('  ANSWER: INSUFFICIENT DATA for realized_vol comparison.')

    w('')
    w('  Q3. Does NOMINAL correspond to objectively stable market conditions?')
    if not rv_row.empty and rv_row.iloc[0]['rank_biserial_r'] > 0 and rv_row.iloc[0]['p_value'] < 0.05:
        w('  ANSWER: YES (by complementarity to Q2).  NOMINAL periods have')
        w('    significantly lower realized volatility than FIREWALL periods.')
    else:
        w('  ANSWER: NOT CLEARLY ESTABLISHED by current tests.')

    w('')
    w('  Q4. Does V12 contain statistically significant predictive information?')
    if not pred_df.empty:
        pred_rv = pred_df[pred_df['label'] == 'realized_vol']
        if not pred_rv.empty:
            best_col = None
            best_rho = 0
            for c in [cc for cc in pred_rv.columns if cc.startswith('rho_k')]:
                v = pred_rv.iloc[0][c]
                if not np.isnan(v) and abs(v) > abs(best_rho):
                    best_rho = v
                    best_col = c
            if best_col:
                p_col = best_col.replace('rho_', 'p_')
                bp    = pred_rv.iloc[0].get(p_col, 1.0)
                sig   = _stars(bp)
                if abs(best_rho) > 0.05 and bp < 0.05:
                    w(f'  ANSWER: YES.  T_sys predicts future realized volatility')
                    w(f'    (best: {best_col}: ρ={best_rho:+.3f}, {sig}).')
                else:
                    w(f'  ANSWER: WEAK/NO.  Predictive correlation is small or')
                    w(f'    not significant (best: {best_col}: ρ={best_rho:+.3f}, {sig}).')
            else:
                w('  ANSWER: UNABLE TO DETERMINE (no predictive data).')
        else:
            w('  ANSWER: realized_vol not found in predictive results.')

    w('')
    w('=' * 72)
    w('END OF REPORT')
    w('=' * 72)

    text = '\n'.join(report_lines)
    report_path = out_dir / 'validation_report.txt'
    report_path.write_text(text, encoding='utf-8')
    print(text)
    return report_path
