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
    echo "Testing domains: $combo"
    python3 -c "
from universal_pde_engine import *
engine = UniversalPDEIntegrator(grid_size=(16,16))
domains = [Domain[d] for d in '$combo'.split(',')]
for domain in domains:
    engine.add_domain(domain, {'test': 1.0})
for step in range(50):
    engine.coupled_pde_step()
print(f'  {combo}: IG={engine.cross_domain_metrics.get(\"information_gravity\",0):.3f}')
print(f'  {combo}: Alignment={engine.cross_domain_metrics.get(\"domain_alignment\",0):.3f}')
"
    echo "---"
done

echo "✅ Cross-domain validation complete"
