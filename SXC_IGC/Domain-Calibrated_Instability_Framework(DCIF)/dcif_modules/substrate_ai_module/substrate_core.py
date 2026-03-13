class SubstrateDynamics:
    def __init__(self):
        self.r, self.a, self.b = 0.153, 1.0, 1.0

    def determine_regime(self, tension):
        if tension < 0.4:
            return 'narrative_ok'     # Safe for local inference
        if tension < 0.7:
            return 'transitional'     # Proceed with high-entropy monitoring
        return 'formal_required'      # Local substrate collapse imminent; offload
