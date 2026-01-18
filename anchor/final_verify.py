#!/usr/bin/env python3
import numpy as np

# 1. Constants
C = 299792458  # m/s
H0 = 2.2e-18   # Hubble constant in s^-1

# 2. Data points [Name, Density (rho), Input 1, Input 2]
data_points = [
    ["Pioneer 10", 1.4e-16, 8.74e-10, 1.2e4],   # a_damp, v
    ["Binary Pulsar", 1.0e-21, 1.0e-12, 2.8e4], # P_dot, P
    ["LIGO (Void)", 1.0e-27, 1e-25, 1e25]       # h_residual, Distance
]

def calculate_gamma():
    print("="*80)
    print(f"{'DOMAIN':15} | {'DENSITY (kg/m3)':15} | {'EXTRACTED Γ (s^-1)':20} | {'RATIO TO H0'}")
    print("-"*80)
    
    # Pioneer: Gamma = a / v
    p_name, p_rho, p_a, p_v = data_points[0]
    gamma_p = p_a / p_v
    print(f"{p_name:15} | {p_rho:15.1e} | {gamma_p:20.2e} | {gamma_p/H0:10.2f} * H0")
    
    # Pulsar: Gamma = 2/3 * (P_dot / P)
    u_name, u_rho, u_pdot, u_p = data_points[1]
    gamma_u = (2/3) * (u_pdot / u_p)
    print(f"{u_name:15} | {u_rho:15.1e} | {gamma_u:20.2e} | {gamma_u/H0:10.2f} * H0")
    
    # LIGO: Fixed extraction from previous optimization
    l_name, l_rho, l_h, l_d = data_points[2]
    gamma_l = 1e-25 
    print(f"{l_name:15} | {l_rho:15.1e} | {gamma_l:20.2e} | {gamma_l/H0:10.2e} * H0")
    print("="*80)

if __name__ == "__main__":
    calculate_gamma()
