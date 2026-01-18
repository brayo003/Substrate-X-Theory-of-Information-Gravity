import os
import json
import matplotlib.pyplot as plt
import numpy as np

def generate_heatmap():
    base_dir = "./dcif_modules"
    modules = []
    tensions = []
    
    # Standardized Stress Scenario for Comparison
    E_test, F_test = 0.5, 0.2 

    for folder in sorted(os.listdir(base_dir)):
        path = os.path.join(base_dir, folder, "coefficients.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                c = data['coefficients']
                T = (c['beta'] * E_test) - (c['gamma'] * F_test)
                modules.append(folder.replace('_module', ''))
                tensions.append(T)

    plt.figure(figsize=(12, 6))
    colors = ['red' if t >= 0.6 else 'orange' if t >= 0.4 else 'green' for t in tensions]
    plt.bar(modules, tensions, color=colors)
    plt.axhline(y=0.6, color='black', linestyle='--', label='Crisis Threshold')
    plt.ylabel('Tension Index (T)')
    plt.title('SXC-IGC v1.0: Global Substrate Instability Heat-Map (E=0.5, F=0.2)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('global_heatmap.png')
    print("Dashboard Generated: global_heatmap.png")

if __name__ == "__main__":
    generate_heatmap()
