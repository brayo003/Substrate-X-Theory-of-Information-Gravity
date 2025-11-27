# k_eff Test Suite

This directory contains versioned tests for different k_eff values across various astrophysical systems.

## Test Categories

### Dwarf Galaxies
- Low surface brightness galaxies
- Ultra-diffuse galaxies
- Dwarf spheroidals

### Spiral Galaxies
- Milky Way analogs
- High-redshift disks
- Barred spirals

### Elliptical Galaxies
- Core vs cusp ellipticals
- Dwarf ellipticals
- Brightest cluster galaxies

### Galaxy Clusters
- Regular clusters
- Cool-core clusters
- Merging systems

## Running Tests

Each subdirectory contains:
- Configuration files
- Analysis scripts
- Expected results

Example:
```bash
cd dwarfs/
python run_dwarf_suite.py --k_eff 0.3
```
