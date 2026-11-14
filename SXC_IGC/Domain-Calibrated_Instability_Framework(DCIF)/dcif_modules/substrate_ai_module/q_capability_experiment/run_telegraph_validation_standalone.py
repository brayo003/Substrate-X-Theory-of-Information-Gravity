"""
Analytical Telegraph-Equation Solver Validation (Standalone)

This script validates the telegraph equation numerical implementation against
analytical solutions using a standalone implementation to avoid import issues.

Theoretical PDE: τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
"""

import numpy as np
import json
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class FieldState:
    """Field state for standalone implementation."""
    field_values: np.ndarray
    field_velocity: np.ndarray
    coordinates: np.ndarray
    dx: float
    dy: float
    dz: float
    dt: float
    physical_time: float
    grid_shape: tuple


@dataclass
class PropagationParameters:
    """Propagation parameters."""
    c_nominal: float = 1.0


@dataclass
class RelaxationParameters:
    """Relaxation parameters."""
    tau_nominal: float = 1.0


def initialize_field_state_1d(x_range=(0.0, 25.0), nx=100, initial_value=1.0, dt=0.01):
    """Initialize 1D field state."""
    x = np.linspace(x_range[0], x_range[1], nx)
    dx = (x_range[1] - x_range[0]) / (nx - 1) if nx > 1 else 1.0
    
    coordinates = np.column_stack([x, np.zeros_like(x)])
    
    field_values = np.full(nx, initial_value)
    field_velocity = np.zeros(nx)
    
    return FieldState(
        field_values=field_values,
        field_velocity=field_velocity,
        coordinates=coordinates,
        dx=dx,
        dy=1.0,
        dz=1.0,
        dt=dt,
        physical_time=0.0,
        grid_shape=(nx, 1, 1),
    )


def evolve_field_telegraph_1d(state, c, tau):
    """Evolve field using telegraph equation (1D implementation)."""
    s = state.field_values
    v = state.field_velocity
    dx = state.dx
    dt = state.dt
    
    # 1D Laplacian
    laplacian = np.zeros_like(s)
    if len(s) > 2:
        laplacian[1:-1] = (s[2:] - 2*s[1:-1] + s[:-2]) / (dx**2)
    
    # Telegraph equation: τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
    # Semi-implicit Euler: v_new = v + dt*(c²∇²s - v/τ)
    acceleration = (c**2) * laplacian - v / tau
    v_new = v + dt * acceleration
    
    # s_new = s + dt*v_new
    s_new = s + dt * v_new
    
    return FieldState(
        s_new, v_new, state.coordinates,
        dx, state.dy, state.dz, dt,
        state.physical_time + dt, state.grid_shape
    )


class TelegraphAnalyticalValidation:
    """Analytical validation of telegraph equation solver."""
    
    def __init__(self):
        self.results = {
            'experiment_date': '2026-08-09',
            'pde': 'τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s',
            'numerical_scheme': 'Semi-implicit Euler: v_new = v + dt*(c²∇²s - v/τ), s_new = s + dt*v_new',
            'test_parameters': {},
            'analytical_solution': {},
            'numerical_results': {},
            'comparison': {},
            'classification': None,
        }
    
    def compute_analytical_solution(self, c, tau, wavelength, A, s0, x, t):
        """Compute analytical telegraph equation solution."""
        k = 2 * np.pi / wavelength
        
        # Check propagating condition
        propagating_condition = c**2 * k**2 > 1/(4 * tau**2)
        
        if propagating_condition:
            omega = np.sqrt(c**2 * k**2 - 1/(4 * tau**2))
        else:
            omega = 0.0  # Overdamped case
        
        # Analytical solution
        s_analytical = s0 + A * np.exp(-t/(2*tau)) * np.cos(k * x - omega * t)
        
        return {
            'k': k,
            'omega': omega,
            'propagating': propagating_condition,
            's_analytical': s_analytical,
            'critical_wavelength': 4 * np.pi * c * tau,
        }
    
    def initialize_controlled_mode_1d(self, nx, wavelength, A, s0, c, tau, dt):
        """Initialize 1D field with controlled sinusoidal mode."""
        print(f"Initializing controlled 1D mode: λ={wavelength}m, A={A}, c={c}m/s, τ={tau}s")
        
        # Compute analytical parameters
        k = 2 * np.pi / wavelength
        omega = np.sqrt(c**2 * k**2 - 1/(4 * tau**2))
        
        # Domain: 1D with 5 wavelengths
        L = 5 * wavelength
        x_range = (0.0, L)
        
        dx = L / (nx - 1)
        
        print(f"Domain: {L}m, Grid: {nx} points, dx={dx:.4f}m")
        print(f"Resolution: {wavelength/dx:.1f} cells/wavelength")
        
        # Initialize field state
        state = initialize_field_state_1d(
            x_range=x_range,
            nx=nx,
            initial_value=s0,
            dt=dt,
        )
        
        # Initialize with sinusoidal mode
        x_coords = state.coordinates[:, 0]
        s_values = s0 + A * np.cos(k * x_coords)
        state.field_values = s_values
        
        # Initialize velocity consistently with analytical solution
        # ∂s/∂t|_(t=0) = A[-1/(2τ) cos(kx) + ω sin(kx)]
        v_values = A * (-1/(2*tau) * np.cos(k * x_coords) + omega * np.sin(k * x_coords))
        state.field_velocity = v_values
        
        return state, k, omega
    
    def measure_fourier_mode_1d(self, state, k, L):
        """Measure Fourier amplitude and phase at selected k."""
        x_coords = state.coordinates[:, 0]
        s_values = state.field_values
        
        # Compute Fourier coefficient at k
        N = len(x_coords)
        dx = L / (N - 1)
        
        # Complex Fourier coefficient
        fourier_coeff = np.sum(s_values * np.exp(-1j * k * x_coords)) * dx / L
        
        amplitude = np.abs(fourier_coeff)
        phase = np.angle(fourier_coeff)
        
        return amplitude, phase
    
    def run_validation(self, c=1.0, tau=1.0, wavelength=5.0, A=0.5, s0=1.0, 
                     resolution_factor=20, duration=10.0, dt=0.01):
        """Run analytical validation experiment."""
        
        print("="*80)
        print("TELEGRAPH EQUATION ANALYTICAL VALIDATION (STANDALONE)")
        print("="*80)
        
        # Store test parameters
        self.results['test_parameters'] = {
            'c': c,
            'tau': tau,
            'wavelength': wavelength,
            'amplitude': A,
            'baseline': s0,
            'resolution_factor': resolution_factor,
            'duration': duration,
            'dt': dt,
        }
        
        # Compute analytical solution parameters
        k = 2 * np.pi / wavelength
        critical_wavelength = 4 * np.pi * c * tau
        omega = np.sqrt(c**2 * k**2 - 1/(4 * tau**2))
        phase_velocity = omega / k
        
        print(f"\nAnalytical parameters:")
        print(f"  k = {k:.4f} rad/m")
        print(f"  ω = {omega:.4f} rad/s")
        print(f"  λ_c = {critical_wavelength:.4f} m")
        print(f"  Phase velocity = {phase_velocity:.4f} m/s")
        print(f"  Propagating condition: c²k² > 1/(4τ²): {c**2 * k**2 > 1/(4 * tau**2)}")
        
        self.results['analytical_solution'] = {
            'k': k,
            'omega': omega,
            'critical_wavelength': critical_wavelength,
            'phase_velocity': phase_velocity,
            'propagating': c**2 * k**2 > 1/(4 * tau**2),
        }
        
        # Grid resolution
        dx = wavelength / resolution_factor
        L = 5 * wavelength
        nx = int(L / dx) + 1
        
        print(f"\nNumerical configuration:")
        print(f"  Domain: {L}m")
        print(f"  Grid: {nx} points")
        print(f"  dx = {dx:.4f}m")
        print(f"  Resolution: {wavelength/dx:.1f} cells/wavelength")
        print(f"  dt = {dt}s")
        print(f"  CFL: {c * dt / dx:.4f}")
        
        # Initialize controlled mode
        state, k_initial, omega_initial = self.initialize_controlled_mode_1d(
            nx, wavelength, A, s0, c, tau, dt
        )
        
        # Time evolution and measurement
        times = []
        amplitudes = []
        phases = []
        numerical_solutions = []
        analytical_solutions = []
        l2_errors = []
        
        current_state = state
        current_time = 0.0
        
        num_steps = int(duration / dt)
        output_interval = max(1, num_steps // 100)  # 100 outputs
        
        print(f"\nTime evolution: {duration}s, {num_steps} steps")
        
        for step in range(num_steps):
            # Record measurements
            if step % output_interval == 0:
                amplitude, phase = self.measure_fourier_mode_1d(current_state, k, L)
                
                times.append(current_time)
                amplitudes.append(amplitude)
                phases.append(phase)
                
                # Store numerical solution
                numerical_solutions.append(current_state.field_values.copy())
                
                # Compute analytical solution
                x_coords = current_state.coordinates[:, 0]
                analytical = s0 + A * np.exp(-current_time/(2*tau)) * np.cos(k * x_coords - omega * current_time)
                analytical_solutions.append(analytical)
                
                # Compute L2 error
                l2_error = np.sqrt(np.mean((current_state.field_values - analytical)**2))
                l2_errors.append(l2_error)
            
            # Evolve field
            current_state = evolve_field_telegraph_1d(current_state, c, tau)
            current_time += dt
        
        # Analyze results
        print(f"\nNumerical results:")
        
        # Convert to numpy arrays
        times = np.array(times)
        amplitudes = np.array(amplitudes)
        phases = np.array(phases)
        l2_errors = np.array(l2_errors)
        
        # Fit damping rate
        ln_amplitudes = np.log(amplitudes)
        damping_coeffs = np.polyfit(times, ln_amplitudes, 1)
        gamma_measured = -damping_coeffs[0]
        tau_measured = 1 / (2 * gamma_measured) if gamma_measured > 0 else 0.0
        
        print(f"  Measured damping rate γ = {gamma_measured:.4f} s⁻¹")
        print(f"  Theoretical damping rate γ = {1/(2*tau):.4f} s⁻¹")
        print(f"  Measured τ = {tau_measured:.4f} s")
        print(f"  Theoretical τ = {tau:.4f} s")
        
        # Fit oscillation frequency
        # Unwrap phases to avoid 2π jumps
        phases_unwrapped = np.unwrap(phases)
        omega_coeffs = np.polyfit(times, phases_unwrapped, 1)
        omega_measured = -omega_coeffs[0]
        
        print(f"  Measured ω = {omega_measured:.4f} rad/s")
        print(f"  Theoretical ω = {omega:.4f} rad/s")
        
        # Phase velocity
        v_phase_measured = omega_measured / k
        print(f"  Measured phase velocity = {v_phase_measured:.4f} m/s")
        print(f"  Theoretical phase velocity = {phase_velocity:.4f} m/s")
        
        # Recover c from measured parameters
        c_recovered = np.sqrt(v_phase_measured**2 + 1/(4 * tau_measured**2 * k**2))
        print(f"  Recovered c = {c_recovered:.4f} m/s")
        print(f"  Theoretical c = {c:.4f} m/s")
        
        # L2 error analysis
        max_l2_error = np.max(l2_errors)
        mean_l2_error = np.mean(l2_errors)
        final_l2_error = l2_errors[-1]
        
        print(f"\nError analysis:")
        print(f"  Max L2 error: {max_l2_error:.6f}")
        print(f"  Mean L2 error: {mean_l2_error:.6f}")
        print(f"  Final L2 error: {final_l2_error:.6f}")
        
        # Store numerical results
        self.results['numerical_results'] = {
            'gamma_measured': gamma_measured,
            'tau_measured': tau_measured,
            'omega_measured': omega_measured,
            'v_phase_measured': v_phase_measured,
            'c_recovered': c_recovered,
            'max_l2_error': max_l2_error,
            'mean_l2_error': mean_l2_error,
            'final_l2_error': final_l2_error,
            'times': times.tolist(),
            'amplitudes': amplitudes.tolist(),
            'phases': phases.tolist(),
            'l2_errors': l2_errors.tolist(),
        }
        
        # Comparison with theory
        tau_error = abs(tau_measured - tau) / tau if tau > 0 else 0
        omega_error = abs(omega_measured - omega) / omega if omega > 0 else 0
        c_error = abs(c_recovered - c) / c if c > 0 else 0
        
        self.results['comparison'] = {
            'tau_error': tau_error,
            'omega_error': omega_error,
            'c_error': c_error,
            'gamma_error': abs(gamma_measured - 1/(2*tau)) / (1/(2*tau)) if tau > 0 else 0,
        }
        
        print(f"\nRelative errors:")
        print(f"  τ error: {tau_error:.2%}")
        print(f"  ω error: {omega_error:.2%}")
        print(f"  c error: {c_error:.2%}")
        print(f"  γ error: {abs(gamma_measured - 1/(2*tau)) / (1/(2*tau)):.2%}")
        
        # Classification
        print(f"\nClassification:")
        
        # Check if solution propagates
        if omega_measured > 0.1 * omega:
            print("  ✓ Solution propagates (ω_measured > 0.1 ω_theory)")
            propagates = True
        else:
            print("  ✗ Solution does not propagate (ω_measured < 0.1 ω_theory)")
            propagates = False
        
        # Check damping agreement
        if tau_error < 0.2:
            print("  ✓ Damping rate matches theory within 20%")
            damping_ok = True
        else:
            print("  ✗ Damping rate does not match theory (error > 20%)")
            damping_ok = False
        
        # Check frequency agreement
        if omega_error < 0.2:
            print("  ✓ Frequency matches theory within 20%")
            frequency_ok = True
        else:
            print("  ✗ Frequency does not match theory (error > 20%)")
            frequency_ok = False
        
        # Check c recovery
        if c_error < 0.2:
            print("  ✓ c recovered within 20%")
            c_ok = True
        else:
            print("  ✗ c not recovered within 20%")
            c_ok = False
        
        # Check numerical stability
        if max_l2_error < 1.0 and not np.any(np.isnan(l2_errors)):
            print("  ✓ Numerically stable")
            stable = True
        else:
            print("  ✗ Numerically unstable or divergent")
            stable = False
        
        # Final classification
        if propagates and damping_ok and frequency_ok and c_ok and stable:
            classification = "A"
            print("\n  FINAL CLASSIFICATION: CASE A")
            print("  Numerical solution propagates and matches analytical solution within expected numerical error.")
        elif propagates and (not damping_ok or not frequency_ok):
            classification = "B"
            print("\n  FINAL CLASSIFICATION: CASE B")
            print("  Numerical solution oscillates but damping/frequency differs substantially from theory.")
        elif not propagates and stable:
            classification = "C"
            print("\n  FINAL CLASSIFICATION: CASE C")
            print("  Numerical solution does not oscillate/propagate despite initial condition being analytically propagating mode.")
        elif not stable:
            classification = "D"
            print("\n  FINAL CLASSIFICATION: CASE D")
            print("  Numerical scheme is unstable.")
        else:
            classification = "E"
            print("\n  FINAL CLASSIFICATION: CASE E")
            print("  Numerical solution appears correct but convergence/refinement fails.")
        
        self.results['classification'] = classification
        
        return classification
    
    def run_refinement_test(self, c=1.0, tau=1.0, wavelength=5.0, A=0.5, s0=1.0, dt=0.01):
        """Run refinement test to check convergence."""
        print("\n" + "="*80)
        print("REFINEMENT TEST")
        print("="*80)
        
        refinement_results = []
        resolution_factors = [10, 20, 40]  # Different resolutions
        
        for resolution_factor in resolution_factors:
            print(f"\nResolution factor: {resolution_factor}")
            
            try:
                # Quick test with shorter duration
                classification = self.run_validation(
                    c=c, tau=tau, wavelength=wavelength, A=A, s0=s0,
                    resolution_factor=resolution_factor, duration=5.0, dt=dt
                )
                
                l2_error = self.results['numerical_results']['final_l2_error']
                refinement_results.append({
                    'resolution_factor': resolution_factor,
                    'classification': classification,
                    'final_l2_error': l2_error,
                })
                
                print(f"  Final L2 error: {l2_error:.6f}")
                
            except Exception as e:
                print(f"  Error: {e}")
                refinement_results.append({
                    'resolution_factor': resolution_factor,
                    'error': str(e),
                })
        
        # Analyze convergence
        valid_results = [r for r in refinement_results if 'final_l2_error' in r]
        
        if len(valid_results) >= 2:
            l2_errors = [r['final_l2_error'] for r in valid_results]
            print(f"\nConvergence analysis:")
            print(f"  L2 errors: {l2_errors}")
            
            if len(l2_errors) >= 2:
                if l2_errors[-1] < l2_errors[0]:
                    print("  ✓ Error decreases with refinement")
                    converges = True
                else:
                    print("  ✗ Error does not decrease with refinement")
                    converges = False
            else:
                converges = None
        else:
            converges = None
        
        self.results['refinement_test'] = {
            'results': refinement_results,
            'converges': converges,
        }
        
        return converges
    
    def save_results(self):
        """Save validation results."""
        print("\n" + "="*80)
        print("SAVING RESULTS")
        print("="*80)
        
        # Convert numpy types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            else:
                return obj
        
        results_serializable = convert_numpy_types(self.results)
        
        # Save JSON
        json_path = '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/q_capability_experiment/telegraph_analytical_validation_results.json'
        with open(json_path, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        print(f"JSON results saved to: {json_path}")
        
        # Save markdown report
        md_path = '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/q_capability_experiment/TELEGRAPH_ANALYTICAL_VALIDATION_RESULTS.md'
        
        with open(md_path, 'w') as f:
            f.write("# Telegraph Equation Analytical Validation Results\n\n")
            f.write(f"**Validation Date:** {results_serializable['experiment_date']}\n\n")
            f.write(f"**PDE:** {results_serializable['pde']}\n\n")
            f.write(f"**Numerical Scheme:** {results_serializable['numerical_scheme']}\n\n")
            f.write(f"**Final Classification:** {results_serializable['classification']}\n\n")
            f.write("---\n\n")
            
            f.write("## Test Parameters\n\n")
            params = results_serializable['test_parameters']
            f.write(f"- c: {params['c']} m/s\n")
            f.write(f"- τ: {params['tau']} s\n")
            f.write(f"- Wavelength: {params['wavelength']} m\n")
            f.write(f"- Amplitude: {params['amplitude']}\n")
            f.write(f"- Baseline: {params['baseline']}\n")
            f.write(f"- Resolution factor: {params['resolution_factor']} cells/wavelength\n")
            f.write(f"- Duration: {params['duration']} s\n")
            f.write(f"- Time step: {params['dt']} s\n\n")
            
            f.write("## Analytical Solution\n\n")
            analytical = results_serializable['analytical_solution']
            f.write(f"- k: {analytical['k']:.4f} rad/m\n")
            f.write(f"- ω: {analytical['omega']:.4f} rad/s\n")
            f.write(f"- Critical wavelength: {analytical['critical_wavelength']:.4f} m\n")
            f.write(f"- Phase velocity: {analytical['phase_velocity']:.4f} m/s\n")
            f.write(f"- Propagating: {analytical['propagating']}\n\n")
            
            f.write("## Numerical Results\n\n")
            numerical = results_serializable['numerical_results']
            f.write(f"- Measured damping rate γ: {numerical['gamma_measured']:.4f} s⁻¹\n")
            f.write(f"- Measured τ: {numerical['tau_measured']:.4f} s\n")
            f.write(f"- Measured ω: {numerical['omega_measured']:.4f} rad/s\n")
            f.write(f"- Measured phase velocity: {numerical['v_phase_measured']:.4f} m/s\n")
            f.write(f"- Recovered c: {numerical['c_recovered']:.4f} m/s\n")
            f.write(f"- Max L2 error: {numerical['max_l2_error']:.6f}\n")
            f.write(f"- Mean L2 error: {numerical['mean_l2_error']:.6f}\n")
            f.write(f"- Final L2 error: {numerical['final_l2_error']:.6f}\n\n")
            
            f.write("## Comparison with Theory\n\n")
            comparison = results_serializable['comparison']
            f.write(f"- τ error: {comparison['tau_error']:.2%}\n")
            f.write(f"- ω error: {comparison['omega_error']:.2%}\n")
            f.write(f"- c error: {comparison['c_error']:.2%}\n")
            f.write(f"- γ error: {comparison['gamma_error']:.2%}\n\n")
            
            f.write("## Classification\n\n")
            classification = results_serializable['classification']
            f.write(f"**{classification}**\n\n")
            
            if classification == "A":
                f.write("CASE A: Numerical solution propagates and matches analytical solution within expected numerical error.\n\n")
            elif classification == "B":
                f.write("CASE B: Numerical solution oscillates but damping/frequency differs substantially from theory.\n\n")
            elif classification == "C":
                f.write("CASE C: Numerical solution does not oscillate/propagate despite initial condition being analytically propagating mode.\n\n")
            elif classification == "D":
                f.write("CASE D: Numerical scheme is unstable.\n\n")
            elif classification == "E":
                f.write("CASE E: Numerical solution appears correct but convergence/refinement fails.\n\n")
            
            if 'refinement_test' in results_serializable:
                f.write("## Refinement Test\n\n")
                refinement = results_serializable['refinement_test']
                f.write(f"Converges: {refinement['converges']}\n\n")
                for result in refinement['results']:
                    if 'error' not in result:
                        f.write(f"- Resolution {result['resolution_factor']}: L2 error = {result['final_l2_error']:.6f}\n")
                    else:
                        f.write(f"- Resolution {result['resolution_factor']}: Error - {result['error']}\n")
        
        print(f"Markdown report saved to: {md_path}")
        
        return results_serializable


def main():
    """Run analytical validation experiment."""
    print("="*80)
    print("TELEGRAPH EQUATION ANALYTICAL VALIDATION (STANDALONE)")
    print("Validating numerical solver against controlled analytical propagating mode")
    print("="*80)
    
    experiment = TelegraphAnalyticalValidation()
    
    # Run main validation
    print("\nRunning main validation...")
    classification = experiment.run_validation(
        c=1.0, tau=1.0, wavelength=5.0, A=0.5, s0=1.0,
        resolution_factor=20, duration=10.0, dt=0.01
    )
    
    # Run refinement test
    print("\nRunning refinement test...")
    convergence = experiment.run_refinement_test(
        c=1.0, tau=1.0, wavelength=5.0, A=0.5, s0=1.0, dt=0.01
    )
    
    # Save results
    print("\nSaving results...")
    experiment.save_results()
    
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)
    print(f"Final classification: {classification}")
    
    return experiment.results


if __name__ == "__main__":
    results = main()
