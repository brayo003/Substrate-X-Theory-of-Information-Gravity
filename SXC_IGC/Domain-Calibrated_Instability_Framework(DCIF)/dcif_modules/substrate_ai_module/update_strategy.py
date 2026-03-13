# V12_SYNC_VERIFIED: 2026-03-13
import re
import os

def apply_calibration(threshold):
    path = 'adaptive_thinker.py'
    with open(path, 'r') as f:
        content = f.read()

    # Regex to find the ABORT threshold check in select_strategy
    # It looks for: if tension > [number]: return ThinkingStrategy.ABORT
    pattern = r"(if tension > )(\d+\.\d+)(: return ThinkingStrategy\.ABORT)"
    new_content = re.sub(pattern, rf"\g<1>{threshold}\g<3>", content)

    with open(path, 'w') as f:
        f.write(new_content)
    print(f"✅ adaptive_thinker.py updated with threshold: {threshold}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        apply_calibration(sys.argv[1])
