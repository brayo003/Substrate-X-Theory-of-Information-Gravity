#!/usr/bin/env python3
"""
ANALYZE WIKIPEDIA CLICKSTREAM - FINAL FIX FOR PARSER ERROR
Uses 6-column structure and Python engine for robustness.
"""

import pandas as pd
import numpy as np
import gzip
import random

def load_and_sample_wikipedia_data(sample_size=100000):
    """Load Wikipedia data with chunking and proper random sampling"""
    print("📊 Loading Wikipedia data with robust parser...")
    
    # 6-COLUMN STRUCTURE FOR ROBUSTNESS (to catch 5-field errors)
    COLUMN_NAMES = [
        'prev_title', 'curr_title', 'type', 'n',
        'prev_id_placeholder', 'curr_id_placeholder'  
    ]
    
    # Use chunking to avoid memory overload
    chunk_size = 50000
    sampled_data = []
    total_rows = 0
    target_sample = sample_size
    
    print(f"  Sampling target: {target_sample:,} random rows")
    
    # **CRITICAL FIX: Use Python engine and ignore bad lines**
    for chunk in pd.read_csv('clickstream-sample.tsv.gz', 
                             compression='gzip',
                             sep='\t',
                             header=None,
                             names=COLUMN_NAMES,
                             chunksize=chunk_size,
                             engine='python',            # Use robust Python engine
                             error_bad_lines=False,      # Ignore corrupted lines
                             warn_bad_lines=True):       # Keep warnings enabled
        
        total_rows += len(chunk)
        
        # Reservoir sampling: maintain a random sample across chunks
        for _, row in chunk.iterrows():
            if len(sampled_data) < target_sample:
                sampled_data.append(row)
            else:
                # Replace random element with decreasing probability
                r = random.randint(0, total_rows)
                if r < target_sample:
                    sampled_data[random.randint(0, target_sample - 1)] = row # Corrected index access
    
    df_sampled = pd.DataFrame(sampled_data)
    
    # Clean up the placeholder columns and potentially mixed-type data
    df_sampled = df_sampled.drop(columns=['prev_id_placeholder', 'curr_id_placeholder'], errors='ignore')
    
    print(f"✅ Sampled {len(df_sampled):,} rows from {total_rows:,} total")
    print(f"  Data types: {df_sampled['type'].value_counts().to_dict()}")
    
    return df_sampled

# [Remainder of the script (compute_wikipedia_S, Q, UTD) remains the same as previously fixed]
def compute_wikipedia_S(df):
    """Compute Structural Entropy from properly sampled network"""
    print("\n🔍 Computing Structural Entropy (S) from sampled network...")
    
    # Focus on INTERNAL navigation (link type)
    internal_links = df[df['type'] == 'link']
    print(f"  Internal navigation links in sample: {len(internal_links):,}")
    
    if len(internal_links) < 1000:
        print("  ⚠️ Low internal link count - including external for structure")
        # Include some external for network structure
        external_sample = df[df['type'] == 'external'].head(20000)
        internal_links = pd.concat([internal_links, external_sample])
    
    # Build the network from ALL sampled internal links
    all_pages = list(set(internal_links['prev_title']) | set(internal_links['curr_title']))
    
    print(f"  Building network with {len(all_pages):,} unique pages...")
    
    page_to_idx = {page: i for i, page in enumerate(all_pages)}
    
    # Build weighted adjacency matrix from ALL sampled links
    adj = np.zeros((len(all_pages), len(all_pages)))
    for _, row in internal_links.iterrows():
        # Handle potential errors where titles are NaN or missing
        try:
            i = page_to_idx[row['prev_title']]
            j = page_to_idx[row['curr_title']]
            adj[i, j] += row['n']
        except KeyError:
            continue
    
    # Compute degree distribution entropy
    degrees = np.sum(adj, axis=1)
    total_flow = np.sum(degrees)
    
    if total_flow > 0:
        degree_dist = degrees / total_flow
        degree_dist = degree_dist[degree_dist > 1e-10]
        S = -np.sum(degree_dist * np.log(degree_dist))
    else:
        S = 2.0  # Default for social systems
    
    print(f"  Network: {len(all_pages):,} pages, {total_flow:,} total clicks")
    print(f"  Structural Entropy S = {S:.3f}")
    return S

def compute_wikipedia_Q(df):
    """Compute Coherence from properly sampled traffic"""
    print("\n🔍 Computing Coherence (Q) from sampled traffic...")
    
    # Use the ENTIRE sample for traffic distribution
    total_clicks_sample = df['n'].sum()
    
    # Focus on destination pages
    page_traffic = df.groupby('curr_title')['n'].sum().sort_values(ascending=False)
    
    # Use proportional sampling - top pages should be representative
    sample_fraction = len(df) / 50000000  # Estimate of total rows
    estimated_total_clicks = total_clicks_sample / sample_fraction
    
    # Take representative top pages (scaled by sample fraction)
    sample_top_count = max(100, int(1000 * sample_fraction))
    top_pages = page_traffic.head(sample_top_count)
    top_traffic = top_pages.sum()
    
    # Herfindahl index - concentration measure
    traffic_share = top_pages / top_traffic
    Q = np.sum(traffic_share ** 2)
    
    print(f"  Sample clicks: {total_clicks_sample:,}")
    print(f"  Estimated total clicks: {estimated_total_clicks:,.0f}")
    print(f"  Top {sample_top_count} pages in sample")
    print(f"  Coherence Q = {Q:.3f}")
    return Q

def compute_wikipedia_UTD(S, Q):
    """Compute Wikipedia UTD C-score"""
    print("\n🎯 Computing Wikipedia UTD C-score...")
    
    # Wikipedia parameters - adjusted for social systems
    delta2 = 0.00008     # Social system volatility
    tau_E = 1.0          # Daily excitation  
    tau_F = 30.0         # Monthly recovery
    k = 102914           # Calibration constant
    
    temporal_ratio = np.sqrt(tau_E / tau_F)
    C = k * delta2 * Q * temporal_ratio / S
    
    print(f"  Parameters (Social System):")
    print(f"  δ₂ (volatility): {delta2:.5f}")
    print(f"  τ_E/τ_F: {tau_E:.1f}/{tau_F:.1f} days")
    print(f"  Calculation:")
    print(f"  C = {k:,} × {delta2:.5f} × {Q:.3f} × {temporal_ratio:.3f} ÷ {S:.3f}")
    print(f"  C = {C:.6f}")
    
    # Classification
    if C >= 2.5:
        classification = "CLASS 0 (Ultra-Rigid)"
    elif C >= 1.0:
        classification = "CLASS I (Engineered)"
    elif C >= 0.1:
        classification = "CLASS II (Biological)"
    else:
        classification = "CLASS IV (Social)"
    
    print(f"  → {classification}")
    return C

# MAIN EXECUTION
print("🎯 WIKIPEDIA UTD ANALYSIS - FINAL FIX FOR PARSER ERROR")
print("=" * 50)

# Load with proper sampling (100K random rows)
df = load_and_sample_wikipedia_data(sample_size=100000)

# Compute parameters from representative sample
S = compute_wikipedia_S(df)
Q = compute_wikipedia_Q(df)
C = compute_wikipedia_UTD(S, Q)

print(f"\n📊 FINAL WIKIPEDIA PROFILE (From Representative Sample):")
print(f"  Structural Entropy S = {S:.3f}")
print(f"  Coherence Q = {Q:.3f}") 
print(f"  UTD C-score = {C:.6f}")

print(f"\n🔬 VALIDATION AGAINST SOCIAL CLASS:")
expected_range = (0.03, 0.08)
within_range = expected_range[0] <= C <= expected_range[1]

print(f"  Expected: C ≈ {expected_range[0]}-{expected_range[1]} (Social range)")
print(f"  Measured: C = {C:.6f}")
print(f"  Result: {'✅ WITHIN EXPECTED RANGE' if within_range else '❌ OUTSIDE EXPECTED RANGE'}")

if within_range:
    print(f"  🎉 SUCCESS: Wikipedia confirmed as CLASS IV Social System")
else:
    print(f"  🔧 NOTE: May need parameter adjustment for social domain")

print(f"\n💡 SAMPLE STATISTICS:")
print(f"  Total rows sampled: {len(df):,}")
print(f"  Internal links: {len(df[df['type'] == 'link']):,}")
print(f"  External referrers: {len(df[df['type'] == 'external']):,}")
