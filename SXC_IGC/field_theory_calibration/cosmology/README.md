# Cosmology Module

This module handles large-scale structure formation and cosmic evolution.

## Components

### Mode Decomposition
- Implements large-scale PDE solutions
- Handles linear and non-linear regimes

### Growth Rate Estimation
- Computes matter power spectrum
- Predicts structure formation rates

### Cosmological Parameters
- Hubble constant
- Matter density parameters
- Dark energy equation of state

## Usage

```python
from cosmology import Cosmology

cosmo = Cosmology(h=0.7, Omega_m=0.3, Omega_lambda=0.7)
growth = cosmo.growth_factor(z=1.0)
```
