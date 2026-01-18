import h5py
import numpy as np

print("=== EXACT FILE STRUCTURE ===")
with h5py.File('H-H1_LOSC_4_V1-1126256640-4096.hdf5', 'r') as f:
    print("1. Top level:")
    for key in f.keys():
        obj = f[key]
        if isinstance(obj, h5py.Group):
            print(f"  Group: {key}")
            # Look inside strain group
            if key == 'strain':
                for subkey in obj.keys():
                    subobj = obj[subkey]
                    if isinstance(subobj, h5py.Dataset):
                        print(f"    Dataset: {subkey}, shape: {subobj.shape}")
                        # Get actual data
                        data = subobj[:]
                        print(f"    First 3 values: {data[:3]}")
                        print(f"    Data type: {data.dtype}")
                    else:
                        print(f"    Sub-group: {subkey}")
        else:
            print(f"  Dataset: {key}, shape: {obj.shape}")
    
    print("\n2. Metadata check:")
    if 'meta' in f:
        meta = f['meta']
        for attr in meta.attrs:
            print(f"  meta.{attr}: {meta.attrs[attr]}")
    
    print("\n3. Getting strain data:")
    if 'strain' in f:
        # Strain is a group, find the dataset inside
        strain_group = f['strain']
        dataset_name = None
        for name in strain_group:
            if isinstance(strain_group[name], h5py.Dataset):
                dataset_name = name
                break
        
        if dataset_name:
            print(f"  Found dataset: strain/{dataset_name}")
            strain_data = strain_group[dataset_name][:]
            print(f"  Shape: {strain_data.shape}")
            print(f"  Mean: {np.mean(strain_data):.2e}")
            print(f"  STD: {np.std(strain_data):.2e}")
            print(f"  Min: {np.min(strain_data):.2e}")
            print(f"  Max: {np.max(strain_data):.2e}")
            
            # Analyze first second as noise
            fs = 4096  # Known sampling rate
            noise = strain_data[:fs]
            print(f"\n  Noise (first {fs} samples):")
            print(f"  Noise STD: {np.std(noise):.2e}")
            print(f"  Noise mean: {np.mean(noise):.2e}")
            
            # Quick Gaussian test
            from scipy.stats import normaltest
            _, p = normaltest(noise)
            print(f"  Gaussian test p-value: {p:.3e}")
            
            # Save raw numbers
            with open('noise_facts.txt', 'w') as out:
                out.write(f"noise_std:{np.std(noise):.6e}\n")
                out.write(f"noise_mean:{np.mean(noise):.6e}\n")
                out.write(f"gaussian_p:{p:.6e}\n")
                out.write(f"full_data_std:{np.std(strain_data):.6e}\n")
                out.write(f"data_length:{len(strain_data)}\n")
            
            print("\n  Saved raw numbers to 'noise_facts.txt'")
            
            # Plot histogram of noise
            import matplotlib.pyplot as plt
            plt.figure(figsize=(10, 4))
            plt.subplot(1, 2, 1)
            plt.hist(noise, bins=50, alpha=0.7)
            plt.xlabel('Strain')
            plt.ylabel('Count')
            plt.title('Noise Distribution')
            
            plt.subplot(1, 2, 2)
            plt.plot(noise[:1000])
            plt.xlabel('Sample')
            plt.ylabel('Strain')
            plt.title('Noise Time Series')
            
            plt.tight_layout()
            plt.savefig('noise_analysis.png', dpi=120)
            print("  Plot saved as 'noise_analysis.png'")
        else:
            print("  ERROR: No dataset found inside strain group")
    else:
        print("  ERROR: No strain group found")
