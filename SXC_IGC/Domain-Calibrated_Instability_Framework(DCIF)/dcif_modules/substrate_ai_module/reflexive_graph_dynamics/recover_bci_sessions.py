from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
import scipy.io

SOURCE = Path("data/nm000139/data.nemar.org/nm000139/v1.0.3/sourcedata")
RECOVERY = Path("data/recovered/bci_iv_2a_original")
TARGETS = ["A06T", "A07T", "A09T", "A09E"]

RECOVERY.mkdir(parents=True, exist_ok=True)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def validate_mat(path):
    mat = scipy.io.loadmat(
        path,
        squeeze_me=True,
        struct_as_record=False
    )
    entries = np.atleast_1d(mat["data"]).ravel()
    return entries

def main():
    results = {}
    for target in TARGETS:
        filename = f"{target}.mat"
        out_path = RECOVERY / filename

        print(f"\n========================================================================")
        print(f"Locating and recovering {filename}")
        print(f"========================================================================")

        if not out_path.exists():
            # Search locally in the SOURCE directory recursively
            found_files = list(SOURCE.glob(f"**/{filename}"))
            if not found_files:
                found_files = list(SOURCE.glob(f"**/{target}*"))

            if found_files:
                src_file = found_files[0]
                print(f"Found locally at {src_file}. Copying to {out_path}...")
                shutil.copy2(src_file, out_path)
            else:
                print(f"Error: {filename} not found locally in {SOURCE}.")
                results[target] = {"status": "error", "error": "file not found locally"}
                continue
        else:
            print(f"Found existing recovery file at {out_path}, skipping copy.")

        file_hash = sha256(out_path)
        print(f"SHA256: {file_hash}")

        try:
            data = validate_mat(out_path)
            print(f"Successfully loaded {filename}. Data entries shape: {data.shape}")
            results[target] = {"status": "success", "sha256": file_hash}
        except Exception as e:
            print(f"Error validating {filename}: {e}")
            results[target] = {"status": "error", "error": str(e), "sha256": file_hash}

    with open("recovery_report.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nRecovery process completed. Report saved to recovery_report.json.")

if __name__ == "__main__":
    main()
