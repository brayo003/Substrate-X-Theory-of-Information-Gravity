# Wikipedia UTD Analysis - Final Results

## Dataset
- **Edges analyzed**: 1,417,585
- **Total clicks**: 137,643,463
- **Unique pages**: 672,769

## UTD Metrics
| Metric | Value | Interpretation |
|--------|-------|----------------|
| **S (Spectral Entropy)** | 1.8568 | Network decentralization |
| **Q (Coherence)** | 0.00006568 | Traffic concentration (HHI) |
| **δ² (Volatility)** | 0.12233091 | Edge weight inequality |
| **C (Information Gravity)** | 2.46 | Overall tension score |

## Top Pages by Traffic
1. **United_States**: 0.1857%
2. **Jimmy_Carter**: 0.1772%
3. **Marvel_Cinematic_Universe:_Phase_Six**: 0.1438%
4. **George_V**: 0.1057%
5. **Rosalynn_Carter**: 0.1016%

## Interpretation
C = 2.46 indicates **STABLE STRUCTURE**.

Wikipedia shows relative decentralization.

## Methodology
1. Processed 1.4M edge sample from Wikipedia clickstream (2023-11)
2. Calculated spectral entropy via randomized SVD (S = 1.8568)
3. Derived Q from traffic distribution (Herfindahl-Hirschman Index)
4. Derived δ² from edge weight distribution (1 - normalized entropy)
5. Combined via geometric mean: C = k × (S × Q × δ²)^(¹/₃)
