#!/usr/bin/env python3
"""
FINAL UTD calculation using your extracted Colab data.
"""
import pandas as pd
import numpy as np
import json
import os

print("🎯 FINAL UTD CALCULATION")
print("=" * 60)

# Load your data
df = pd.read_parquet("data/processed/real_triplets.parquet")
print(f"📊 Data: {len(df):,} edges, {df['src'].nunique():,} unique pages")

# 1. Calculate REAL Q (Coherence)
print("\n1. 🎯 CALCULATING Q (COHERENCE)")
incoming = df.groupby('dst')['count'].sum()
outgoing = df.groupby('src')['count'].sum()

# Combine traffic per page
traffic = pd.concat([incoming, outgoing]).groupby(level=0).sum()
total_traffic = traffic.sum()

# Herfindahl-Hirschman Index
proportions = traffic / total_traffic
Q = (proportions ** 2).sum()

print(f"   ✅ Q = {Q:.8f}")
print(f"   Total traffic: {total_traffic:,}")
print(f"   Pages with traffic: {len(traffic):,}")

# Top pages
top5 = proportions.nlargest(5)
print(f"   🏆 Top 5 pages:")
for page, share in top5.items():
    print(f"     {page[:50]:50} {share:.4%}")

# 2. Calculate REAL delta2 (Volatility)
print("\n2. ⚡ CALCULATING delta2 (VOLATILITY)")
weights = df['count'].values
total_weight = weights.sum()

# Weight entropy method
p = weights / total_weight
H = -np.sum(p * np.log2(p + 1e-10))
H_max = np.log2(len(p))
H_norm = H / H_max if H_max > 0 else 0
delta2 = 1 - H_norm  # 0 = uniform, 1 = concentrated

print(f"   ✅ delta2 = {delta2:.8f}")
print(f"   Weight entropy: {H:.2f}/{H_max:.2f} bits")
print(f"   Normalized: {H_norm:.4f}")

# 3. Use your calculated S
S = 1.8568  # From your Colab spectral entropy calculation
print(f"\n3. 🔮 USING S (SPECTRAL ENTROPY) = {S:.4f}")

# 4. Calculate C-score
print("\n4. 🧮 CALCULATING C-SCORE")
C_raw = (S * Q * delta2) ** (1/3)  # Geometric mean

# Scale for interpretability (0-100 range)
k = 100
C = k * C_raw

print(f"   Raw C = {C_raw:.6f}")
print(f"   ✅ SCALED C = {C:.2f}")

# 5. Interpretation
print(f"\n5. 📊 INTERPRETATION")
print(f"   S = {S:.4f} (network decentralization)")
print(f"   Q = {Q:.8f} (traffic concentration)")
print(f"   delta2 = {delta2:.8f} (weight inequality)")
print(f"   C = {C:.2f} (overall information gravity)")

if C > 70:
    print(f"\n   🚨 HIGH INFORMATION GRAVITY")
    print("   Wikipedia shows strong centralization and concentration.")
elif C > 30:
    print(f"\n   ⚠️  MODERATE TENSION")
    print("   Balanced between centralization and diversity.")
else:
    print(f"\n   ✅ STABLE STRUCTURE")
    print("   Relatively decentralized and diverse.")

# 6. Compare with placeholder
print(f"\n6. 📈 COMPARISON")
print(f"   Old C (with placeholders): 132,679,651.87")
print(f"   Real C (proper calculation): {C:,.2f}")
print(f"   Difference: 132 million → {C:,.2f}")
print(f"   That's {132679651.87/C:,.0f}x more realistic!")

# 7. Save results
print(f"\n7. 💾 SAVING RESULTS")
results = {
    'S_spectral_entropy': float(S),
    'Q_coherence': float(Q),
    'delta2_volatility': float(delta2),
    'C_raw': float(C_raw),
    'C_scaled': float(C),
    'data_stats': {
        'n_edges': int(len(df)),
        'total_weight': float(df['count'].sum()),
        'unique_pages': int(df['src'].nunique()),
        'top_pages': {str(k): float(v) for k, v in top5.items()}
    }
}

os.makedirs("results", exist_ok=True)
with open("results/utd_final_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"✅ Results saved to: results/utd_final_results.json")

# Create markdown summary
with open("results/analysis_summary.md", "w") as f:
    f.write(f"""# Wikipedia UTD Analysis - Final Results

## Dataset
- **Edges analyzed**: {len(df):,}
- **Total clicks**: {df['count'].sum():,}
- **Unique pages**: {df['src'].nunique():,}

## UTD Metrics
| Metric | Value | Interpretation |
|--------|-------|----------------|
| **S (Spectral Entropy)** | {S:.4f} | Network decentralization |
| **Q (Coherence)** | {Q:.8f} | Traffic concentration (HHI) |
| **δ² (Volatility)** | {delta2:.8f} | Edge weight inequality |
| **C (Information Gravity)** | {C:.2f} | Overall tension score |

## Top Pages by Traffic
""")
    
    for i, (page, share) in enumerate(top5.items(), 1):
        f.write(f"{i}. **{page}**: {share:.4%}\n")
    
    f.write(f"""
## Interpretation
C = {C:.2f} indicates {"**HIGH INFORMATION GRAVITY**" if C > 70 else "**MODERATE TENSION**" if C > 30 else "**STABLE STRUCTURE**"}.

Wikipedia shows {"strong centralization" if C > 70 else "moderate centralization" if C > 30 else "relative decentralization"}.

## Methodology
1. Processed 1.4M edge sample from Wikipedia clickstream (2023-11)
2. Calculated spectral entropy via randomized SVD (S = {S:.4f})
3. Derived Q from traffic distribution (Herfindahl-Hirschman Index)
4. Derived δ² from edge weight distribution (1 - normalized entropy)
5. Combined via geometric mean: C = k × (S × Q × δ²)^(¹/₃)
""")

print(f"✅ Summary saved to: results/analysis_summary.md")
print(f"\n🎉 ANALYSIS COMPLETE!")
