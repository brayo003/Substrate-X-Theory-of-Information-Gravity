import requests

# Validated Solid Tissue Normal miRNA ID for TCGA-LUAD
file_id = "07f90870-7613-401d-932d-209630a103c8" 
url = f"https://api.gdc.cancer.gov/data/{file_id}"

print(f"REQUESTING SUBSTRATE: {file_id}")
response = requests.get(url, stream=True)

if response.status_code == 200:
    import os
    os.makedirs("raw_data", exist_ok=True)
    with open("raw_data/normal_lung_control.txt", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
    print("SUCCESS: Substrate 'normal_lung_control.txt' internalized.")
else:
    print(f"CRITICAL ERROR: API returned status {response.status_code}")
    print(f"MESSAGE: {response.text}")
