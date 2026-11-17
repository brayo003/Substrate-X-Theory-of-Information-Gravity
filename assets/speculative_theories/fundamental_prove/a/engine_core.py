import numpy as np

def sxc_drift(x, r=0.153267, a=1.0, b=1.0):
    """The unique cubic potential derivative: f(I) = rI + aI^2 - bI^3"""
    return r*x + a*x**2 - b*x**3

def get_bit_cost(x, limit=1.5):
    """The relational metric cost function C(I)"""
    # Prevents division by zero at the hard saturation bound
    return 1.0 / (np.maximum(1e-6, limit - np.abs(x)))**0.5
