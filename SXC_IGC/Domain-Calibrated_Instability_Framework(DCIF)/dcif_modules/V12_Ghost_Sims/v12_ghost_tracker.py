import pandas as pd
import numpy as np

class V12GhostTracker:
    def __init__(self, filename="lhc_real_data.csv"):
        self.filename = filename
        self.limit = 10**10 

    def track_leaks(self):
        # Load and immediately strip whitespace from headers
        df = pd.read_csv(self.filename, on_bad_lines='skip', low_memory=False)
        df.columns = df.columns.str.strip()
        
        # Verify required columns exist after stripping
        required = ['px1', 'py1', 'px2', 'py2', 'pt1', 'pt2']
        if not all(col in df.columns for col in required):
            print(f"❌ DATA INCONSISTENCY: Missing columns. Available: {list(df.columns)}")
            return

        # Convert to numeric
        for col in required:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=required)

        # 1. Identify Ghost Candidates
        df['flux'] = df['pt1'] + df['pt2']
        # T = F / gamma^2 where gamma=0.0001
        df['tension'] = (df['flux'] / 0.0001**2)
        ghosts = df[df['tension'] > self.limit].copy()

        # 2. Calculate Missing Transverse Energy (MET)
        # Vector Sum of Muon Pair. Negative sum = the 'Ghost' push
        ghosts['met_x'] = -(ghosts['px1'] + ghosts['px2'])
        ghosts['met_y'] = -(ghosts['py1'] + ghosts['py2'])
        ghosts['met_total'] = np.sqrt(ghosts['met_x']**2 + ghosts['met_y']**2)

        print(f"⚛️ GHOST TRACKER: ANALYZING {len(ghosts)} EXTREME EVENTS")
        print("-" * 50)
        
        if len(ghosts) == 0:
            print("No events crossed the 10^10 Tension threshold.")
            return

        # 3. Verdict
        avg_leak = ghosts['met_total'].mean()
        total_leak = ghosts['met_total'].sum()

        print(f"Average Information Leak (MET): {avg_leak:.2f} GeV")
        print(f"Total Information Lost to Bulk: {total_leak:,.2f} GeV")
        
        print("\n[TOP 5 SHATTER SAMPLES]")
        samples = ghosts.sort_values(by='tension', ascending=False).head(5)
        for _, row in samples.iterrows():
            print(f"Event {int(row['Event'])}: Tension={row['tension']:.2e} | Leak={row['met_total']:.2f} GeV")

if __name__ == "__main__":
    V12GhostTracker().track_leaks()
