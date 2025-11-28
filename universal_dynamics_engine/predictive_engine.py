import numpy as np
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from .universal_pde_engine import UniversalDynamicsEngine, Domain
from .data_coupler import DataCoupler, DomainType

class PredictiveEngine:
    """Predictive engine using the working DataCoupler"""
    
    def __init__(self):
        self.engine = UniversalDynamicsEngine()
        self.prediction_history = []
        
    def train_on_historical_data(self, financial_data, biological_data):
        """Train using the proven DataCoupler"""
        print("🧠 Training PredictiveEngine...")
        
        # Add domains to engine
        self.engine.add_domain(Domain.FINANCE)
        self.engine.add_domain(Domain.BIO_PHYSICS)
        
        # Use DataCoupler to process data - CORRECT USAGE
        financial_coupler = DataCoupler(domain_type=DomainType.FINANCIAL)
        finance_metrics = financial_coupler.ingest_data(financial_data).output_metrics()
        
        bio_coupler = DataCoupler(domain_type=DomainType.BIOLOGICAL)  
        bio_metrics = bio_coupler.ingest_data(biological_data).output_metrics()
        
        print(f"📊 Financial metrics keys: {list(finance_metrics.keys())}")
        print(f"🧬 Biological metrics keys: {list(bio_metrics.keys())}")
        
        # Convert to engine format and inject
        self._inject_data_into_engine(finance_metrics, bio_metrics)
        
        # Run training simulation
        for step in range(50):
            self.engine.integrator.coupled_pde_step()
            if step % 10 == 0:
                tensions = self._get_domain_tensions()
                print(f"   Step {step}: Tensions = {tensions}")
            
        print("✅ Training completed")
        return self
    
    def _inject_data_into_engine(self, finance_metrics, bio_metrics):
        """Inject processed data into engine domains"""
        domains = list(self.engine.integrator.domain_states.values())
        
        # Convert metrics to concentration grids
        finance_grid = self._metrics_to_grid(finance_metrics)
        bio_grid = self._metrics_to_grid(bio_metrics)
        
        domains[0].concentrations = finance_grid  # Finance domain
        domains[1].concentrations = bio_grid      # Bio domain
        
        print(f"🔧 Injected data - Finance grid: {finance_grid.shape}, Bio grid: {bio_grid.shape}")
    
    def _metrics_to_grid(self, metrics):
        """Convert metrics dictionary to 16x16 concentration grid"""
        # Extract numeric values from metrics
        values = []
        for key, val in metrics.items():
            if key != 'features_used' and isinstance(val, dict):
                # For mean/std/var dictionaries, take average
                values.extend(list(val.values()))
            elif isinstance(val, (int, float)):
                values.append(val)
        
        # Create 16x16 grid
        grid_size = 16
        target_size = grid_size * grid_size
        
        if len(values) < target_size:
            # Pad with zeros
            padded = np.zeros(target_size)
            padded[:len(values)] = values[:target_size]
            return padded.reshape(grid_size, grid_size)
        else:
            # Truncate to fit
            return np.array(values[:target_size]).reshape(grid_size, grid_size)
    
    def _get_domain_tensions(self):
        """Get current tensions from all domains"""
        return [domain.metrics['Tension'] 
                for domain in self.engine.integrator.domain_states.values()]
    
    def predict_stress_probability(self, days_ahead=7):
        """Make stress prediction"""
        print(f"🔮 Predicting stress probability for {days_ahead} days...")
        
        future_tensions = []
        for day in range(days_ahead):
            self.engine.integrator.coupled_pde_step()
            avg_tension = np.mean(self._get_domain_tensions())
            future_tensions.append(avg_tension)
        
        stress_prob = self._calculate_stress_probability(future_tensions)
        
        prediction = {
            'days_ahead': days_ahead,
            'stress_probability': stress_prob,
            'future_tensions': future_tensions
        }
        
        self.prediction_history.append(prediction)
        print(f"   Predicted stress probability: {stress_prob:.3f}")
        return prediction
    
    def _calculate_stress_probability(self, future_tensions):
        """Calculate stress probability from tension trajectory"""
        if len(future_tensions) < 4:
            return 0.0
            
        baseline = np.mean(future_tensions[:3])
        peak = max(future_tensions[3:])
        
        increase_ratio = (peak - baseline) / baseline if baseline > 0 else 0
        return min(0.95, max(0.0, increase_ratio))

if __name__ == "__main__":
    # Quick test
    engine = PredictiveEngine()
    print("✅ PredictiveEngine ready for integration")
