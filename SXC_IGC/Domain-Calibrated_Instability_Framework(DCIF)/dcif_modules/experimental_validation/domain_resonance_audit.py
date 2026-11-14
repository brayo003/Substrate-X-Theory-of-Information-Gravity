import pandas as pd
import numpy as np

def analyze_csv():
    df = pd.read_csv('domain_scales.csv')
    
    # Critical Damping occurs at gamma = 2.0 (for beta=1.0)
    # We define 'Q-Factor' (Quality of Resonance) = 1 / gamma
    df['Q_Factor'] = 1 / df['gamma']
    
    # Identify the state
    conditions = [
        (df['gamma'] < 2.0),
        (df['gamma'] == 2.0),
        (df['gamma'] > 2.0)
    ]
    choices = ['Underdamped (Oscillates)', 'Critically Damped', 'Overdamped (Sluggish)']
    df['Dynamics'] = np.select(conditions, choices, default='Unknown')

    print("=== GLOBAL DOMAIN RESONANCE AUDIT ===")
    print(df[['domain', 'gamma', 'Q_Factor', 'Dynamics']].sort_values(by='gamma'))

analyze_csv()
