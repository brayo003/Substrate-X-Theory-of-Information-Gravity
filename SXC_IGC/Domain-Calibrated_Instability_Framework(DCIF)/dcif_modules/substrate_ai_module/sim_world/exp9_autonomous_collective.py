#!/usr/bin/env python3
"""Task 9 entry point — autonomous substrate-mediated collective computation."""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for p in (_PARENT, _HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from sim_world.exp9.runner import main


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    result = main(phase)
    acc = result.get("acceptance") or result.get("acceptance_preview") or {}
    print("phase:", result.get("phase"))
    print("acceptance_level:", acc.get("acceptance_level"))
    print("reasons:", acc.get("reasons"))
