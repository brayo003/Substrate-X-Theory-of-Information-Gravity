import json
import pandas as pd
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def analyze_substrate(path, b=1.5, g=0.8):
    df = pd.read_csv(path, sep='\t')
    signals = StandardScaler().fit_transform(df['read_count'].values.reshape(-1, 1)).flatten()
    engine = SXCOmegaEngine(beta=b, gamma=g)
    return sum([engine.step(abs(s)*5)[0] for s in signals[:1000]])

# 1. Baseline Extraction
normal_tax = analyze_substrate('raw_data/normal_lung_control.txt')
cancer_tax = analyze_substrate('raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt')

# 2. Rescue Calculation (Finding Gamma that matches Normal Tax)
rescue_gamma = 0.8
for g in [0.85, 0.90, 0.95, 1.00, 1.05]:
    if analyze_substrate('raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt', 1.5, g) <= normal_tax:
        rescue_gamma = g
        break

# 3. Report Compilation
report = {
    "module": "Domain-Calibrated_Instability_Framework(DCIF)",
    "tissue_type": "Lung (TCGA-LUAD)",
    "metrics": {
        "healthy_baseline_tax": round(normal_tax, 2),
        "observed_malignant_tax": round(cancer_tax, 2),
        "persistence_delta_pct": round(((cancer_tax/normal_tax)-1)*100, 2)
    },
    "diagnostic_verdict": "CRITICAL_SATURATION" if cancer_tax > 50 else "STABLE",
    "recommended_intervention": {
        "target_regulatory_drain_gamma": rescue_gamma,
        "required_efficacy_increase": round(((rescue_gamma/0.8)-1)*100, 2)
    }
}

with open('patient_health_report.json', 'w') as f:
    json.dump(report, f, indent=4)

print("SUCCESS: 'patient_health_report.json' generated.")
print(json.dumps(report, indent=4))
