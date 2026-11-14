#!/usr/bin/env python3
"""
Q REFERENCE IMPLEMENTATION
Minimal independent implementation of theoretical Q equation from q_define.txt

This implementation:
- Follows q_define.txt exactly
- Makes minimal assumptions
- Uses only mathematically justified operations
- Is independent of the production implementation
"""

import numpy as np
from typing import Tuple, Callable, Optional


class QReference:
    """
    Reference implementation of Q = 4c²τ²|∇ln s|² − 1
    
    Based on q_define.txt definition:
    - s(x,t): scalar information density field (info/m³)
    - c: propagation speed (m/s)
    - τ: damping time constant (s)
    - ∇: spatial gradient in physical coordinates
    - Q: dimensionless transport regime classifier
    """
    
    def __init__(self, c: float, tau: float):
        """
        Initialize Q calculator with physical parameters.
        
        Parameters:
        -----------
        c : float
            Propagation speed in m/s (must be positive)
        tau : float
            Damping time constant in s (must be positive)
        """
        if c <= 0:
            raise ValueError(f"c must be positive, got {c}")
        if tau <= 0:
            raise ValueError(f"tau must be positive, got {tau}")
        
        self.c = c
        self.tau = tau
        
    def compute_gradient_central(self, s: np.ndarray, dx: float = 1.0, axis: int = 0) -> np.ndarray:
        """
        Compute spatial gradient using central finite differences.
        
        Parameters:
        -----------
        s : np.ndarray
            Scalar field values
        dx : float
            Spacing between spatial points (default 1.0)
        axis : int
            Axis along which to compute gradient
            
        Returns:
        --------
        np.ndarray
            Gradient values (same shape as s)
        """
        gradient = np.zeros_like(s)
        
        # Central difference for interior points
        gradient[1:-1] = (s[2:] - s[:-2]) / (2 * dx)
        
        # Forward difference for first point
        gradient[0] = (s[1] - s[0]) / dx
        
        # Backward difference for last point
        gradient[-1] = (s[-1] - s[-2]) / dx
        
        return gradient
    
    def compute_log_gradient(self, s: np.ndarray, gradient_s: np.ndarray) -> np.ndarray:
        """
        Compute ∇ln(s) = ∇s / s
        
        Parameters:
        -----------
        s : np.ndarray
            Scalar field values (must be positive)
        gradient_s : np.ndarray
            Gradient of s
            
        Returns:
        --------
        np.ndarray
            Logarithmic gradient values
        """
        if np.any(s <= 0):
            raise ValueError("s must be positive everywhere for ln(s)")
        
        return gradient_s / s
    
    def compute_squared_magnitude(self, gradient_log_s: np.ndarray) -> float:
        """
        Compute |∇ln s|² (squared magnitude of logarithmic gradient)
        
        For 1D: |∇ln s|² = (∇ln s)²
        For higher dimensions: |∇ln s|² = sum of squared components
        
        Parameters:
        -----------
        gradient_log_s : np.ndarray
            Logarithmic gradient (can be scalar or vector)
            
        Returns:
        --------
        float
            Squared magnitude
        """
        return np.sum(gradient_log_s**2)
    
    def compute_q_point(self, s_point: float, gradient_s_point: float) -> Tuple[float, dict]:
        """
        Compute Q at a single point.
        
        Parameters:
        -----------
        s_point : float
            Scalar field value at point (must be positive)
        gradient_s_point : float
            Gradient of s at point
            
        Returns:
        --------
        tuple (Q, diagnostics)
            Q : float
                Computed Q value
            diagnostics : dict
                Intermediate values for verification
        """
        # Compute logarithmic gradient at point
        gradient_log_s_point = gradient_s_point / s_point
        
        # Compute squared magnitude
        squared_magnitude = gradient_log_s_point**2
        
        # Compute Q
        Q = 4.0 * (self.c**2) * (self.tau**2) * squared_magnitude - 1.0
        
        diagnostics = {
            'gradient_s': gradient_s_point,
            'gradient_log_s': gradient_log_s_point,
            'squared_magnitude': squared_magnitude,
            'c': self.c,
            'tau': self.tau
        }
        
        return Q, diagnostics
    
    def compute_q_field(self, s_field: np.ndarray, dx: float = 1.0) -> np.ndarray:
        """
        Compute Q field over spatial domain.
        
        Parameters:
        -----------
        s_field : np.ndarray
            Scalar field values over space
            Shape: (n_spatial,)
        dx : float
            Spacing between spatial points
            
        Returns:
        --------
        np.ndarray
            Q field values (same shape as s_field)
        """
        # Compute gradient field
        gradient_s = self.compute_gradient_central(s_field, dx)
        
        # Compute logarithmic gradient field
        gradient_log_s = self.compute_log_gradient(s_field, gradient_s)
        
        # Compute squared magnitude field
        squared_magnitude = gradient_log_s**2
        
        # Compute Q field
        Q_field = 4.0 * (self.c**2) * (self.tau**2) * squared_magnitude - 1.0
        
        return Q_field


class AnalyticTestFields:
    """
    Analytic test fields with known gradients and Q values.
    Used for numerical verification.
    """
    
    @staticmethod
    def constant_field(x: np.ndarray, A: float = 1.0) -> np.ndarray:
        """
        Constant field: s(x) = A
        
        Expected: ∇s = 0, ∇ln(s) = 0, Q = -1
        """
        return np.full_like(x, A)
    
    @staticmethod
    def linear_field(x: np.ndarray, A: float = 1.0, B: float = 0.1) -> np.ndarray:
        """
        Linear field: s(x) = A + Bx
        
        Expected: ∇s = B, ∇ln(s) = B/(A+Bx), Q = 4c²τ²(B/(A+Bx))² - 1
        """
        return A + B * x
    
    @staticmethod
    def exponential_field(x: np.ndarray, A: float = 1.0, k: float = 0.1) -> np.ndarray:
        """
        Exponential field: s(x) = A * exp(kx)
        
        Expected: ∇s = Ak*exp(kx), ∇ln(s) = k, Q = 4c²τ²k² - 1
        """
        return A * np.exp(k * x)
    
    @staticmethod
    def gaussian_field(x: np.ndarray, A: float = 1.0, mu: float = 0.0, sigma: float = 1.0) -> np.ndarray:
        """
        Gaussian field: s(x) = A * exp(-(x-μ)²/(2σ²))
        
        Expected: ∇s = -A*(x-μ)/σ² * exp(-(x-μ)²/(2σ²))
        ∇ln(s) = -(x-μ)/σ²
        """
        return A * np.exp(-(x - mu)**2 / (2 * sigma**2))
    
    @staticmethod
    def power_law_field(x: np.ndarray, A: float = 1.0, n: float = 2.0) -> np.ndarray:
        """
        Power law field: s(x) = A * x^n
        
        Expected: ∇s = A*n*x^(n-1), ∇ln(s) = n/x, Q = 4c²τ²(n/x)² - 1
        """
        # Avoid x=0
        x_safe = np.where(x == 0, 1e-10, x)
        return A * np.power(x_safe, n)


def analytic_q_linear(x: float, A: float, B: float, c: float, tau: float) -> float:
    """
    Analytic Q for linear field s(x) = A + Bx
    
    Q = 4c²τ²(B/(A+Bx))² - 1
    """
    s = A + B * x
    if s <= 0:
        raise ValueError("s must be positive")
    
    gradient_log_s = B / s
    squared_magnitude = gradient_log_s**2
    Q = 4.0 * (c**2) * (tau**2) * squared_magnitude - 1.0
    
    return Q


def analytic_q_exponential(k: float, c: float, tau: float) -> float:
    """
    Analytic Q for exponential field s(x) = A * exp(kx)
    
    Q = 4c²τ²k² - 1 (independent of x and A)
    """
    squared_magnitude = k**2
    Q = 4.0 * (c**2) * (tau**2) * squared_magnitude - 1.0
    
    return Q


def analytic_q_gaussian(x: float, mu: float, sigma: float, c: float, tau: float) -> float:
    """
    Analytic Q for Gaussian field s(x) = A * exp(-(x-μ)²/(2σ²))
    
    Q = 4c²τ²((x-μ)/σ²)² - 1
    """
    gradient_log_s = -(x - mu) / (sigma**2)
    squared_magnitude = gradient_log_s**2
    Q = 4.0 * (c**2) * (tau**2) * squared_magnitude - 1.0
    
    return Q


if __name__ == "__main__":
    # Quick test
    print("Q Reference Implementation Test")
    print("=" * 50)
    
    # Create reference calculator
    c = 1.0  # m/s
    tau = 0.5  # s
    q_calc = QReference(c, tau)
    
    # Test on exponential field
    x = np.linspace(0, 10, 100)
    s_field = AnalyticTestFields.exponential_field(x, A=1.0, k=0.1)
    
    Q_computed, diagnostics = q_calc.compute_q(s_field, dx=x[1]-x[0])
    Q_analytic = analytic_q_exponential(k=0.1, c=c, tau=tau)
    
    print(f"Computed Q: {Q_computed:.6f}")
    print(f"Analytic Q: {Q_analytic:.6f}")
    print(f"Difference: {abs(Q_computed - Q_analytic):.6e}")
    
    print("\nReference implementation test complete.")
