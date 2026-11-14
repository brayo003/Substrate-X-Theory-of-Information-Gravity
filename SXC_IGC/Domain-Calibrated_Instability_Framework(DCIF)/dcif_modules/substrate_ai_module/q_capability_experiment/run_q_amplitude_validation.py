"""
Amplitude-Dependent Q Validation Experiment

This script determines whether the theoretical Q's predicted regime boundary
changes with amplitude while the telegraph transport regime remains governed by k.

Theoretical Q: Q = 4 c² τ² |∇ln(s)|² - 1
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


class AmplitudeQValidation:
    """Q validation across amplitude variations."""
    
    def __init__(self):
        self.results = {
            'experiment_date': '2026-08-09',
            'theoretical_Q': 'Q = 4 c² τ² |∇ln s|² - 1',
            'pde': 'τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s',
            'dispersion_relation': 'ω² = c²k² - 1/(4τ²)',
            'telegraph_boundary': 'k_c = 1/(2cτ)',
            'fixed_parameters': {},
            'amplitude_sweep': [],
            'analysis': {},
            'conclusion': None,
        }
    
    def compute_analytical_transport(self, c, tau, k):
        """Compute analytical telegraph transport classification."""
        k_c = 1.0 / (2 * c * tau)
        
        propagating = c**2 * k**2 > 1.0 / (4 * tau**2)
        
        if k > k_c:
            regime = "coherent"
        elif k < k_c:
            regime = "overdamped"
        else:
            regime = "critical"
        
        if propagating:
            omega = np.sqrt(c**2 * k**2 - 1.0 / (4 * tau**2))
        else:
            omega = 0.0
        
        return {
            'k_c': k_c,
            'propagating': propagating,
            'regime': regime,
            'omega': omega,
        }
    
    def initialize_fourier_mode(self, k, A, s0, c, tau, nx, dt):
        """Initialize field with controlled Fourier mode."""
        wavelength = 2 * np.pi / k
        L = 5 * wavelength
        x_range = (0.0, L)
        
        dx = L / (nx - 1)
        
        state = initialize_field_state_1d(
            x_range=x_range,
            nx=nx,
            initial_value=s0,
            dt=dt,
        )
        
        # Initialize with Fourier mode
        x_coords = state.coordinates[:, 0]
        s_values = s0 + A * np.cos(k * x_coords)
        state.field_values = s_values
        
        # Initialize velocity consistently with analytical solution
        analytical = self.compute_analytical_transport(c, tau, k)
        omega = analytical['omega']
        
        if analytical['propagating']:
            v_values = A * (-1.0/(2*tau) * np.cos(k * x_coords) + omega * np.sin(k * x_coords))
        else:
            v_values = np.zeros_like(x_coords)
        
        state.field_velocity = v_values
        
        return state, wavelength, analytical
    
    def measure_fourier_mode(self, state, k, L):
        """Measure Fourier amplitude and phase at known k."""
        x_coords = state.coordinates[:, 0]
        s_values = state.field_values
        
        C = np.sum(s_values * np.cos(k * x_coords)) * (L / len(x_coords))
        S = np.sum(s_values * np.sin(k * x_coords)) * (L / len(x_coords))
        
        F = C + 1j * S
        
        amplitude = np.abs(F)
        phase = np.angle(F)
        
        return amplitude, phase
    
    def run_single_experiment(self, c, tau, k, A, s0, resolution_factor=20, duration=5.0, dt=0.01):
        """Run single (k, A) experiment."""
        
        analytical = self.compute_analytical_transport(c, tau, k)
        
        wavelength = 2 * np.pi / k
        nx = int(5 * wavelength * resolution_factor) + 1
        
        state, wavelength_actual, analytical = self.initialize_fourier_mode(k, A, s0, c, tau, nx, dt)
        L = 5 * wavelength_actual
        
        # Time evolution
        times = []
        amplitudes = []
        phases = []
        
        current_state = state
        current_time = 0.0
        
        num_steps = int(duration / dt)
        output_interval = max(1, num_steps // 50)
        
        for step in range(num_steps):
            if step % output_interval == 0:
                amplitude, phase = self.measure_fourier_mode(current_state, k, L)
                times.append(current_time)
                amplitudes.append(amplitude)
                phases.append(phase)
            
            current_state = evolve_field_telegraph_1d(current_state, c, tau)
            current_time += dt
        
        # Analyze results
        times = np.array(times)
        amplitudes = np.array(amplitudes)
        phases = np.array(phases)
        
        # Fit damping rate
        ln_amplitudes = np.log(amplitudes)
        damping_coeffs = np.polyfit(times, ln_amplitudes, 1)
        gamma_measured = -damping_coeffs[0]
        tau_measured = 1.0 / (2 * gamma_measured) if gamma_measured > 0 else 0.0
        
        # Fit oscillation frequency
        phases_unwrapped = np.unwrap(phases)
        omega_coeffs = np.polyfit(times, phases_unwrapped, 1)
        omega_measured = abs(omega_coeffs[0])
        
        # Independent transport classification based on measured ω
        if omega_measured > 0.1:
            measured_transport = "coherent"
        elif omega_measured < 0.05:
            measured_transport = "overdamped"
        else:
            measured_transport = "critical"
        
        # Compute Q from actual field
        x_coords = current_state.coordinates[:, 0]
        s_final = current_state.field_values
        
        ds_dx = np.zeros_like(s_final)
        if len(s_final) > 2:
            ds_dx[1:-1] = (s_final[2:] - s_final[:-2]) / (2 * current_state.dx)
        
        gradient_ln_s = ds_dx / s_final
        gradient_ln_s_squared = gradient_ln_s**2
        
        q_values = 4.0 * (c**2) * (tau**2) * gradient_ln_s_squared - 1.0
        
        q_min = np.min(q_values)
        q_max = np.max(q_values)
        q_mean = np.mean(q_values)
        
        # Q regime classification
        q_regime = "coherent" if q_mean > 0 else "overdamped" if q_mean < 0 else "critical"
        
        # Agreement
        agreement = (q_regime == measured_transport)
        
        result = {
            'k': k,
            'A': A,
            'analytical_transport': analytical['regime'],
            'measured_transport': measured_transport,
            'omega_measured': omega_measured,
            'q_min': q_min,
            'q_max': q_max,
            'q_mean': q_mean,
            'q_regime': q_regime,
            'agreement': agreement,
            'nx': nx,
            'dx': current_state.dx,
        }
        
        return result
    
    def run_amplitude_sweep(self, c=1.0, tau=1.0, s0=1.0):
        """Run amplitude sweep across multiple k values."""
        
        k_values = [0.25, 0.40, 0.50, 0.60, 0.75, 1.00, 1.2566]
        amplitudes = [0.05, 0.10, 0.20, 0.40, 0.60, 0.80]
        
        k_c = 1.0 / (2 * c * tau)
        
        print("="*80)
        print("AMPLITUDE SWEEP")
        print("="*80)
        print(f"Theoretical k_c = {k_c:.4f} rad/m")
        print(f"Testing k: {k_values}")
        print(f"Testing A: {amplitudes}")
        
        self.results['fixed_parameters'] = {
            'c': c,
            'tau': tau,
            's0': s0,
            'k_c': k_c,
        }
        
        sweep_results = []
        
        for k in k_values:
            for A in amplitudes:
                print(f"\nk={k:.4f}, A={A:.2f}")
                
                try:
                    result = self.run_single_experiment(
                        c=c, tau=tau, k=k, A=A, s0=s0,
                        resolution_factor=20, duration=5.0, dt=0.01
                    )
                    sweep_results.append(result)
                    print(f"  Transport: {result['measured_transport']}, Q={result['q_mean']:.4f} ({result['q_regime']})")
                except Exception as e:
                    print(f"  Error: {e}")
                    sweep_results.append({
                        'k': k,
                        'A': A,
                        'error': str(e),
                    })
        
        self.results['amplitude_sweep'] = sweep_results
        return sweep_results
    
    def analyze_q_boundary_by_amplitude(self, sweep_results):
        """Analyze how Q transition boundary changes with amplitude."""
        
        amplitudes = sorted(set([r['A'] for r in sweep_results if 'A' in r]))
        
        print("\n" + "="*80)
        print("Q BOUNDARY ANALYSIS BY AMPLITUDE")
        print("="*80)
        
        boundary_analysis = []
        
        for A in amplitudes:
            results_at_A = [r for r in sweep_results if r.get('A') == A and 'q_mean' in r]
            
            if len(results_at_A) >= 2:
                # Find where Q changes sign
                results_sorted = sorted(results_at_A, key=lambda x: x['k'])
                
                k_transition = None
                for i in range(len(results_sorted) - 1):
                    if results_sorted[i]['q_mean'] * results_sorted[i+1]['q_mean'] < 0:
                        k_transition = (results_sorted[i]['k'] + results_sorted[i+1]['k']) / 2
                        break
                
                boundary_analysis.append({
                    'A': A,
                    'k_transition': k_transition,
                })
                
                if k_transition:
                    print(f"A={A:.2f}: Q transition at k={k_transition:.4f} rad/m")
                else:
                    print(f"A={A:.2f}: No Q transition detected")
        
        return boundary_analysis
    
    def analyze_transport_independence(self, sweep_results):
        """Analyze whether transport classification is amplitude-independent."""
        
        k_values = sorted(set([r['k'] for r in sweep_results if 'k' in r]))
        
        print("\n" + "="*80)
        print("TRANSPORT INDEPENDENCE ANALYSIS")
        print("="*80)
        
        transport_analysis = []
        
        for k in k_values:
            results_at_k = [r for r in sweep_results if r.get('k') == k and 'measured_transport' in r]
            
            if len(results_at_k) > 0:
                transports = set([r['measured_transport'] for r in results_at_k])
                consistent = len(transports) == 1
                
                transport_analysis.append({
                    'k': k,
                    'transports': list(transports),
                    'consistent': consistent,
                })
                
                print(f"k={k:.4f}: Transports={transports}, Consistent={consistent}")
        
        return transport_analysis
    
    def compute_conclusion(self, boundary_analysis, transport_analysis, k_c):
        """Compute final scientific conclusion."""
        
        print("\n" + "="*80)
        print("CONCLUSION ANALYSIS")
        print("="*80)
        
        # Check if transport is amplitude-independent
        transport_consistent = all([a['consistent'] for a in transport_analysis])
        
        # Check if Q boundary is amplitude-independent
        k_transitions = [b['k_transition'] for b in boundary_analysis if b['k_transition'] is not None]
        
        if len(k_transitions) >= 2:
            k_transition_std = np.std(k_transitions)
            k_transition_mean = np.mean(k_transitions)
            q_boundary_amplitude_dependent = k_transition_std > 0.05  # Arbitrary threshold
        else:
            q_boundary_amplitude_dependent = True  # Can't determine
            k_transition_std = None
            k_transition_mean = None
        
        # Compare Q boundary with telegraph boundary
        if k_transition_mean is not None:
            boundary_deviation = abs(k_transition_mean - k_c) / k_c
        else:
            boundary_deviation = 1.0  # Max deviation
        
        print(f"Transport amplitude-independent: {transport_consistent}")
        print(f"Q boundary amplitude-dependent: {q_boundary_amplitude_dependent}")
        print(f"Q boundary mean: {k_transition_mean:.4f} rad/m" if k_transition_mean else "Q boundary mean: None")
        print(f"Q boundary std: {k_transition_std:.4f} rad/m" if k_transition_std else "Q boundary std: None")
        print(f"Telegraph k_c: {k_c:.4f} rad/m")
        print(f"Boundary deviation: {boundary_deviation:.2%}")
        
        # Determine conclusion
        if transport_consistent and not q_boundary_amplitude_dependent and boundary_deviation < 0.1:
            conclusion = "STRUCTURALLY CONSISTENT"
        elif transport_consistent and q_boundary_amplitude_dependent:
            conclusion = "STRUCTURAL MISMATCH"
        elif not transport_consistent:
            conclusion = "INCONCLUSIVE"
        else:
            conclusion = "INCONCLUSIVE"
        
        print(f"\nFINAL CONCLUSION: {conclusion}")
        
        return {
            'transport_consistent': transport_consistent,
            'q_boundary_amplitude_dependent': q_boundary_amplitude_dependent,
            'k_transition_mean': k_transition_mean,
            'k_transition_std': k_transition_std,
            'boundary_deviation': boundary_deviation,
            'conclusion': conclusion,
        }
    
    def save_results(self):
        """Save validation results."""
        
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
        json_path = '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/q_capability_experiment/q_amplitude_validation_results.json'
        with open(json_path, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        print(f"\nJSON results saved to: {json_path}")
        
        # Save markdown report
        md_path = '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/SXC_IGC/Domain-Calibrated_Instability_Framework(DCIF)/dcif_modules/substrate_ai_module/q_capability_experiment/Q_AMPLITUDE_VALIDATION_RESULTS.md'
        
        with open(md_path, 'w') as f:
            f.write("# Q Amplitude Validation Results\n\n")
            f.write(f"**Validation Date:** {results_serializable['experiment_date']}\n\n")
            f.write(f"**Theoretical Q:** {results_serializable['theoretical_Q']}\n\n")
            f.write(f"**PDE:** {results_serializable['pde']}\n\n")
            f.write(f"**Telegraph Boundary:** {results_serializable['telegraph_boundary']}\n\n")
            f.write(f"**Conclusion:** {results_serializable['conclusion']}\n\n")
            f.write("---\n\n")
            
            f.write("## Fixed Parameters\n\n")
            params = results_serializable['fixed_parameters']
            f.write(f"- c: {params['c']} m/s\n")
            f.write(f"- τ: {params['tau']} s\n")
            f.write(f"- s0: {params['s0']}\n")
            f.write(f"- Telegraph k_c: {params['k_c']:.4f} rad/m\n\n")
            
            f.write("## Amplitude Sweep Results\n\n")
            f.write("| k | A | Analytical Transport | Measured Transport | Q Mean | Q Regime | Agreement |\n")
            f.write("|---|---|---------------------|-------------------|--------|----------|----------|\n")
            
            for result in results_serializable['amplitude_sweep']:
                if 'error' not in result:
                    f.write(f"| {result['k']:.4f} | {result['A']:.2f} | {result['analytical_transport']} | {result['measured_transport']} | {result['q_mean']:.4f} | {result['q_regime']} | {result['agreement']} |\n")
            
            f.write("\n## Q Boundary Analysis\n\n")
            if 'boundary_analysis' in results_serializable['analysis']:
                for ba in results_serializable['analysis']['boundary_analysis']:
                    if ba['k_transition']:
                        f.write(f"- A={ba['A']:.2f}: Q transition at k={ba['k_transition']:.4f} rad/m\n")
                    else:
                        f.write(f"- A={ba['A']:.2f}: No Q transition detected\n")
            
            f.write("\n## Transport Independence Analysis\n\n")
            if 'transport_analysis' in results_serializable['analysis']:
                for ta in results_serializable['analysis']['transport_analysis']:
                    f.write(f"- k={ta['k']:.4f}: Transports={ta['transports']}, Consistent={ta['consistent']}\n")
            
            f.write("\n## Conclusion\n\n")
            analysis = results_serializable['analysis']
            f.write(f"Transport amplitude-independent: {analysis['transport_consistent']}\n")
            f.write(f"Q boundary amplitude-dependent: {analysis['q_boundary_amplitude_dependent']}\n")
            if analysis['k_transition_mean']:
                f.write(f"Q boundary mean: {analysis['k_transition_mean']:.4f} rad/m\n")
                f.write(f"Q boundary std: {analysis['k_transition_std']:.4f} rad/m\n")
            f.write(f"Boundary deviation from k_c: {analysis['boundary_deviation']:.2%}\n\n")
            
            f.write(f"**Final Conclusion:** {analysis['conclusion']}\n\n")
            
            f.write("---\n\n")
            f.write("## EXPERIMENTAL RESULT\n\n")
            f.write("Is the current theoretical Q structurally compatible with the telegraph equation's independently measurable propagation regime across changes in field amplitude?\n\n")
            
            if analysis['conclusion'] == "STRUCTURALLY CONSISTENT":
                f.write("**Answer: YES**\n\n")
            elif analysis['conclusion'] == "STRUCTURAL MISMATCH":
                f.write("**Answer: NO**\n\n")
            else:
                f.write("**Answer: INCONCLUSIVE**\n\n")
        
        print(f"Markdown report saved to: {md_path}")
        
        return results_serializable


def main():
    """Run amplitude validation experiment."""
    print("="*80)
    print("AMPLITUDE-DEPENDENT Q VALIDATION EXPERIMENT")
    print("Testing whether Q boundary changes with amplitude")
    print("="*80)
    
    experiment = AmplitudeQValidation()
    
    # Run amplitude sweep
    print("\nRunning amplitude sweep...")
    sweep_results = experiment.run_amplitude_sweep(c=1.0, tau=1.0, s0=1.0)
    
    # Analyze Q boundary by amplitude
    print("\nAnalyzing Q boundary by amplitude...")
    boundary_analysis = experiment.analyze_q_boundary_by_amplitude(sweep_results)
    experiment.results['analysis']['boundary_analysis'] = boundary_analysis
    
    # Analyze transport independence
    print("\nAnalyzing transport independence...")
    transport_analysis = experiment.analyze_transport_independence(sweep_results)
    experiment.results['analysis']['transport_analysis'] = transport_analysis
    
    # Compute conclusion
    print("\nComputing conclusion...")
    k_c = 1.0 / (2 * 1.0 * 1.0)  # c=1.0, tau=1.0
    conclusion_analysis = experiment.compute_conclusion(boundary_analysis, transport_analysis, k_c)
    experiment.results['analysis'].update(conclusion_analysis)
    experiment.results['conclusion'] = conclusion_analysis['conclusion']
    
    # Save results
    print("\nSaving results...")
    results = experiment.save_results()
    
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)
    print(f"Final conclusion: {conclusion_analysis['conclusion']}")
    
    return experiment.results


if __name__ == "__main__":
    results = main()
