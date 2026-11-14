import pandas as pd

def process():
    try:
        # Load the French grid data (Semicolon separated)
        df = pd.read_csv('nuclear_flux.csv', sep=';', names=['Date', 'Time', 'MW'])
        df['MW'] = pd.to_numeric(df['MW'], errors='coerce')
        df = df.dropna(subset=['MW'])
        
        t_sys = 0.0
        gamma = 0.08 
        baseline = df['MW'].iloc[0]
        
        print(f"{'Time':<10} | {'MW Output':<10} | {'T_sys':<10} | {'State'}")
        print("-" * 50)
        
        for i, row in df.iterrows():
            mw = row['MW']
            # Symmetry Break = Change in the energy state of the substrate
            injection = abs(mw - baseline) / baseline
            t_sys = (injection * 200) + (t_sys * (1 - gamma))
            
            state = "SHATTER" if t_sys > 1.0 else "NOMINAL"
            label = f"*** {state} ***" if state == "SHATTER" else state
            print(f"{row['Time']:<10} | {mw:<10.0f} | {t_sys:<10.4f} | {label}")
            baseline = mw
            
    except Exception as e:
        print(f"Logic Error: {e}")

process()
