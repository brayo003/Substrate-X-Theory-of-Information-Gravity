#!/usr/bin/env python3
"""
SXC-IGC Local Client for Colab GPU Endpoint Service

This script runs on your local machine and connects to the Colab GPU service
via HTTP requests through an ngrok tunnel.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional


class SXCIGCClient:
    """Client for SXC-IGC Colab GPU service."""
    
    def __init__(self, base_url: str):
        """
        Initialize client with Colab endpoint URL.
        
        Args:
            base_url: The ngrok/public URL of the Colab service (e.g., https://random-name.ngrok-free.dev)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        try:
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_health(self) -> Dict[str, Any]:
        """Get health check."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def test_inference(self, entity_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test inference with EntityContext.
        
        Args:
            entity_context: Dictionary with entity state (location, hunger, thirst, energy)
        
        Returns:
            Inference results including reasoning, intent, goal, action, latency
        """
        try:
            response = self.session.post(
                f"{self.base_url}/test_inference",
                json={"entity_context": entity_context},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def run_simulation(
        self,
        world_name: str = "canonical-run",
        ticks: int = 10,
        entities: int = 5,
        seed: str = "local-client-test"
    ) -> Dict[str, Any]:
        """
        Run simulation on Colab GPU.
        
        Args:
            world_name: World configuration name
            ticks: Number of simulation ticks
            entities: Number of entities
            seed: Random seed for reproducibility
        
        Returns:
            Simulation status
        """
        try:
            response = self.session.post(
                f"{self.base_url}/run_simulation",
                json={
                    "world_name": world_name,
                    "ticks": ticks,
                    "entities": entities,
                    "seed": seed
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_simulation_status(self) -> Dict[str, Any]:
        """Get simulation status."""
        try:
            response = self.session.get(f"{self.base_url}/simulation_status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def wait_for_simulation(self, poll_interval: int = 5, timeout: int = 3600) -> Dict[str, Any]:
        """
        Wait for simulation to complete.
        
        Args:
            poll_interval: Seconds between status checks
            timeout: Maximum wait time in seconds
        
        Returns:
            Final simulation result
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_simulation_status()
            
            if "error" in status:
                return status
            
            if status.get("status") == "idle" and "ticks_completed" in status:
                return status
            
            print(f"Simulation running... (elapsed: {int(time.time() - start_time)}s)")
            time.sleep(poll_interval)
        
        return {"error": "Timeout waiting for simulation completion"}


def main():
    """Main client interaction."""
    if len(sys.argv) < 2:
        print("Usage: python sxc_igc_client.py <ngrok_url>")
        print("Example: python sxc_igc_client.py https://random-name.ngrok-free.dev")
        sys.exit(1)
    
    base_url = sys.argv[1]
    client = SXCIGCClient(base_url)
    
    print("=" * 80)
    print("SXC-IGC LOCAL CLIENT")
    print("=" * 80)
    print(f"Connecting to: {base_url}")
    
    # Test connection
    print("\n1. Testing connection...")
    status = client.get_status()
    print(f"Status: {json.dumps(status, indent=2)}")
    
    if "error" in status:
        print(f"✗ Connection failed: {status['error']}")
        sys.exit(1)
    
    print("✓ Connection successful")
    
    # Health check
    print("\n2. Health check...")
    health = client.get_health()
    print(f"Health: {json.dumps(health, indent=2)}")
    
    if health.get("gpu"):
        print(f"✓ GPU detected: {health['gpu']}")
    else:
        print("⚠ GPU not detected or model not loaded")
    
    # Test inference
    print("\n3. Testing inference...")
    test_context = {
        "location": "forest_edge",
        "hunger": 0.7,
        "thirst": 0.3,
        "energy": 0.8
    }
    
    inference_result = client.test_inference(test_context)
    print(f"Inference result: {json.dumps(inference_result, indent=2)}")
    
    if inference_result.get("success"):
        print(f"✓ Inference successful")
        print(f"  Latency: {inference_result['latency_ms']:.2f}ms")
        print(f"  Intent: {inference_result['intent']}")
        print(f"  Action: {inference_result['action']}")
    else:
        print(f"✗ Inference failed: {inference_result.get('error')}")
    
    # Run simulation
    print("\n4. Running simulation...")
    sim_result = client.run_simulation(
        world_name="canonical-run",
        ticks=10,
        entities=5,
        seed="local-client-test"
    )
    print(f"Simulation started: {json.dumps(sim_result, indent=2)}")
    
    if "error" in sim_result:
        print(f"✗ Simulation failed to start: {sim_result['error']}")
        sys.exit(1)
    
    print("✓ Simulation started in background")
    
    # Wait for completion
    print("\n5. Waiting for simulation completion...")
    final_result = client.wait_for_simulation(poll_interval=5, timeout=600)
    print(f"Final result: {json.dumps(final_result, indent=2)}")
    
    if final_result.get("success"):
        print("✓ Simulation completed successfully")
        print(f"  Ticks completed: {final_result['ticks_completed']}")
        print(f"  Entities: {final_result['entity_count']}")
        print(f"  Duration: {final_result['duration_seconds']:.2f}s")
        print(f"  Output: {final_result['output_directory']}")
    else:
        print(f"✗ Simulation failed: {final_result.get('error')}")
    
    print("\n" + "=" * 80)
    print("CLIENT SESSION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()