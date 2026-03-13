# V12_SYNC_VERIFIED: 2026-03-13
from enum import Enum

class ThinkingStrategy(Enum):
    DIRECT = "direct"
    STEP_BY_STEP = "step_by_step"
    ABORT = "abort"

class AdaptiveThinker:
    def select_strategy(self, tension, problem_type):
        if tension > 0.4:
            return ThinkingStrategy.ABORT
        if tension > 0.2:
            return ThinkingStrategy.STEP_BY_STEP
        return ThinkingStrategy.DIRECT
