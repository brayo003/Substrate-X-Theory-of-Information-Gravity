import json

class DomainGuard:
    def __init__(self):
        # Explicit Coupling Ontology
        # Only these channels are 'physically' or 'logically' possible.
        self.adjacencies = {
            "finance_module": ["macroeconomics", "logistics", "social_module", "cybersecurity"],
            "macroeconomics": ["finance_module", "logistics", "agriculture", "energy_sector"],
            "logistics": ["finance_module", "macroeconomics", "telecom", "manufacturing"],
            "seismic_module": ["geophysics", "civil_engineering", "atmospheric_science"],
            "atmospheric_science": ["seismic_module", "agriculture", "oceanography"],
            "cybersecurity": ["finance_module", "telecom", "social_module", "defense_systems"],
            "social_module": ["finance_module", "cybersecurity", "game_module", "public_health"],
            "dark_matter": ["astrophysics", "cosmology"],
            "paleontology": ["geology", "evolutionary_biology"]
        }

    def is_coupling_allowed(self, source, target):
        """Final Check: Do these domains actually share a physical/logical interface?"""
        allowed_targets = self.adjacencies.get(source, [])
        return target in allowed_targets

if __name__ == "__main__":
    guard = DomainGuard()
    print("ONTOLOGICAL CHECK: Finance -> Seismic")
    print(f"Allowed: {guard.is_coupling_allowed('finance_module', 'seismic_module')}")
    
    print("\nONTOLOGICAL CHECK: Finance -> Macroeconomics")
    print(f"Allowed: {guard.is_coupling_allowed('finance_module', 'macroeconomics')}")
