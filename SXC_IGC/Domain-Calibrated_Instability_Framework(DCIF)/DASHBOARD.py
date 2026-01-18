import matplotlib.pyplot as plt
import pandas as pd
import re
import os

def parse_logs(file_path):
    data = []
    # Pattern: Timestamp | Max-T | Phase | Soc-T
    pattern = re.compile(r"(\d{2}:\d{2}:\d{2})\s*\|\s*([\d.]+)\s*\|\s*(\w+)\s*\|\s*([\d.]+)")
    
    if not os.path.exists(file_path):
        return pd.DataFrame()

    with open(file_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                data.append({
                    "max_t": float(match.group(2)),
                    "phase": match.group(3),
                    "soc_t": float(match.group(4))
                })
    return pd.DataFrame(data)

def render_dashboard(df):
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(12, 7))

    # X-axis setup
    x = range(len(df))

    # Plot Global Max Tension
    ax1.plot(x, df['max_t'], color='#00ffcc', label='Global Max Tension (T_max)', linewidth=2.5, zorder=3)
    
    # Plot Social Substrate Tension
    ax1.plot(x, df['soc_t'], color='#ff00ff', label='Social Substrate (T_soc)', linewidth=1.5, linestyle='--', zorder=4)

    # Threshold Overlays
    ax1.axhline(y=1.0, color='#ff4444', linestyle=':', alpha=0.8, label='Firewall Threshold (1.0)')
    ax1.axhline(y=0.4, color='#ffbb33', linestyle=':', alpha=0.8, label='Hysteresis Floor (0.4)')

    # Phase Shading (Visualizes the Schmitt Trigger duration)
    ax1.fill_between(x, 0, max(df['max_t'])*1.1, where=(df['phase'] == 'FIREWALL'), 
                    color='red', alpha=0.15, label='FIREWALL Active')
    
    ax1.fill_between(x, 0, max(df['max_t'])*1.1, where=(df['phase'] == 'PREDICTIVE'), 
                    color='yellow', alpha=0.05, label='PREDICTIVE Active')

    # Formatting
    ax1.set_title('SXC-IGC Stability Analysis: V8_FINAL Recovery Arc', fontsize=14, pad=20)
    ax1.set_xlabel('Simulation Steps (dt=0.05)', fontsize=12)
    ax1.set_ylabel('Information Gravity Tension ($T$)', fontsize=12)
    ax1.set_ylim(0, max(df['max_t']) * 1.2)
    
    ax1.legend(loc='upper right', frameon=True, facecolor='#222222', edgecolor='#444444')
    ax1.grid(True, which='both', linestyle='--', alpha=0.1)

    plt.tight_layout()
    plt.savefig('SXC_Stability_Report.png')
    print("\n[SUCCESS] Dashboard rendered to SXC_Stability_Report.png")
    plt.show()

if __name__ == "__main__":
    log_file = 'stability.log'
    df = parse_logs(log_file)
    if not df.empty:
        render_dashboard(df)
    else:
        print(f"[ERROR] No valid data found in {log_file}. Ensure the engine output is redirected correctly.")
