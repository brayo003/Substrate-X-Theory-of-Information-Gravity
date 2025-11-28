#!/bin/bash

echo "🔬 CROSS-DOMAIN VALIDATION TEST"
echo "================================"

# Test with different domain combinations
DOMAIN_COMBINATIONS=(
    "BIO_PHYSICS,FINANCE"
    "BIO_PHYSICS,FINANCE,ENERGY"
    "BIO_PHYSICS,FINANCE,ENERGY,PLANETARY"
)

for combo in "${DOMAIN_COMBINATIONS[@]}"; do
    echo "---"
    echo "Testing domains: $combo"
    python3 -c "
from universal_pde_engine import UniversalPDEIntegrator, Domain
engine = UniversalPDEIntegrator(grid_size=(16,16))
# Safely parse the domain names from the shell variable
domains = [Domain[d] for d in '$combo'.split(',')] 
for domain in domains:
    engine.add_domain(domain, {'test': 1.0})

# Evolve the system 50 steps
for step in range(50):
    ig_score, alignment, anomalies, uri_signal = engine.coupled_pde_step()

ig = engine.cross_domain_metrics.get('information_gravity', 0.0)
alignment = engine.cross_domain_metrics.get('domain_alignment', 0.0)

# Validation Check: IG should remain high (>= 0.90) regardless of alignment
if ig >= 0.90:
    validation_status = '✅ IG Stability Confirmed'
else:
    validation_status = '❌ IG Stability FAILED'

print(f'  Metrics: IG={ig:.4f}, Alignment={alignment:.4f}')
print(f'  Validation: {validation_status}')
"
done

echo "---"
echo "✅ Cross-domain validation complete"
