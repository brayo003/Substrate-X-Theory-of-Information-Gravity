import urllib.request
import os

# Using a verified mirror for CMS Real Collision Data
url = "https://raw.githubusercontent.com/particle-physics-playground/bptoolkit/master/data/dimuon_data.csv"
output = "cms_real_collisions.csv"

print(f"⚛️ V13 DATA ACQUISITION: Attempting Mirror Retrieval...")

headers = {'User-Agent': 'Mozilla/5.0'}
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        content = response.read()
        with open(output, 'wb') as f:
            f.write(content)
    size = os.path.getsize(output) / (1024 * 1024)
    if size < 0.1:
        print(f"❌ FAILED: File too small ({size:.2f} MB). Still hitting a placeholder.")
    else:
        print(f"✅ SUCCESS: {output} saved ({size:.2f} MB).")
except Exception as e:
    print(f"❌ FAILED: {e}")
