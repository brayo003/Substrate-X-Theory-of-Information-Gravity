import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

class RealTimeReactionDiffusion:
    """Real-time visualization of Turing pattern formation"""
    
    def __init__(self, grid_size=(80, 80)):
        self.grid_size = grid_size
        self.dx = 1.0 / (grid_size[0] - 1)
        self.dy = 1.0 / (grid_size[1] - 1)
        
        # Parameters for clear pattern formation
        self.Du = 0.0002
        self.Dv = 0.01
        self.a = 0.1
        self.b = 0.9
        self.dt = 0.5 * min(self.dx**2, self.dy**2) / (4 * max(self.Du, self.Dv))
        
        # Initialize concentrations
        u0 = self.a + self.b
        v0 = self.b / (u0**2)
        self.u = np.ones(grid_size) * u0
        self.v = np.ones(grid_size) * v0
        
        # Add structured perturbations
        xx, yy = np.meshgrid(np.linspace(0, 2*np.pi, grid_size[0]), 
                            np.linspace(0, 2*np.pi, grid_size[1]))
        noise = 0.005 * np.random.normal(0, 1, grid_size)
        low_freq = 0.003 * (np.sin(4*xx) + np.sin(4*yy))
        self.u += noise + low_freq
        self.v += noise + low_freq
        
        self.time = 0.0
        self.step_count = 0
        
        print("🎬 REAL-TIME PATTERN FORMATION")
        print("   Watch the patterns emerge live!")
    
    def laplacian_2d(self, u):
        """Calculate 2D Laplacian"""
        laplacian = np.zeros_like(u)
        laplacian[1:-1, 1:-1] = (
            (u[1:-1, 2:] - 2*u[1:-1, 1:-1] + u[1:-1, 0:-2]) / self.dx**2 +
            (u[2:, 1:-1] - 2*u[1:-1, 1:-1] + u[0:-2, 1:-1]) / self.dy**2
        )
        # Neumann boundaries
        laplacian[0, :] = laplacian[1, :]
        laplacian[-1, :] = laplacian[-2, :]
        laplacian[:, 0] = laplacian[:, 1]
        laplacian[:, -1] = laplacian[:, -2]
        return laplacian
    
    def step(self):
        """Single simulation step"""
        lap_u = self.laplacian_2d(self.u)
        lap_v = self.laplacian_2d(self.v)
        
        u2v = self.u**2 * self.v
        f = self.a - self.u + u2v
        g = self.b - u2v
        
        self.u += self.dt * (self.Du * lap_u + f)
        self.v += self.dt * (self.Dv * lap_v + g)
        
        self.u = np.maximum(self.u, 0.001)
        self.v = np.maximum(self.v, 0.001)
        
        self.time += self.dt
        self.step_count += 1
    
    def run_real_time(self, total_steps=5000, update_interval=50):
        """Run with real-time visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Initial plots
        im1 = ax1.imshow(self.u, cmap='viridis', animated=True)
        ax1.set_title('Activator (u) - Pattern Formation')
        plt.colorbar(im1, ax=ax1)
        
        im2 = ax2.imshow(self.v, cmap='plasma', animated=True)
        ax2.set_title('Inhibitor (v)')
        plt.colorbar(im2, ax=ax2)
        
        variance_history = []
        time_history = []
        
        def update(frame):
            # Run multiple steps between updates for speed
            for _ in range(update_interval):
                self.step()
                if self.step_count >= total_steps:
                    return im1, im2
            
            # Update plots
            im1.set_array(self.u)
            im2.set_array(self.v)
            
            # Update titles with current info
            variance = np.var(self.u)
            variance_history.append(variance)
            time_history.append(self.time)
            
            ax1.set_title(f'Activator - Step {self.step_count}\nTime: {self.time:.1f}, Variance: {variance:.6f}')
            ax2.set_title(f'Inhibitor - Step {self.step_count}')
            
            print(f"Step {self.step_count}: Time={self.time:.1f}, Variance={variance:.6f}")
            
            return im1, im2
        
        # Create animation
        ani = FuncAnimation(fig, update, frames=total_steps//update_interval, 
                          interval=100, blit=False, repeat=False)
        
        plt.tight_layout()
        plt.show()
        
        return ani

# Run real-time visualization
if __name__ == "__main__":
    print("Starting real-time pattern formation...")
    print("This will open a window showing the pattern emergence live!")
    print("Close the window to stop the simulation.")
    
    simulator = RealTimeReactionDiffusion(grid_size=(80, 80))
    simulator.run_real_time(total_steps=8000, update_interval=100)
