import requests
import json
import os

# 1. Search for available Normal Substrates
filters = {
    "op": "and",
    "content":[
        {"op": "in", "content": {"field": "cases.project.project_id", "value": ["TCGA-LUAD"]}},
        {"op": "in", "content": {"field": "cases.samples.sample_type", "value": ["Solid Tissue Normal"]}},
        {"op": "in", "content": {"field": "files.data_type", "value": ["miRNA Expression Quantification"]}},
        {"op": "in", "content": {"field": "files.access", "value": ["open"]}}
    ]
}

params = {"filters": json.dumps(filters), "fields": "file_id", "format": "JSON", "size": "1"}
response = requests.get("https://api.gdc.cancer.gov/files", params=params)

if response.status_code == 200:
    hits = response.json()['data']['hits']
    if not hits:
        print("CRITICAL: No Normal substrates found.")
        exit()
    
    target_id = hits[0]['file_id']
    print(f"FOUND VALID NORMAL SUBSTRATE: {target_id}")
    
    # 2. Download the Substrate
    data_url = f"https://api.gdc.cancer.gov/data/{target_id}"
    data_res = requests.get(data_url)
    
    if data_res.status_code == 200:
        os.makedirs("raw_data", exist_ok=True)
        with open("raw_data/normal_lung_control.txt", "wb") as f:
            f.write(data_res.content)
        print("SUCCESS: Substrate internalized to raw_data/normal_lung_control.txt")
    else:
        print(f"FAILED DOWNLOAD: {data_res.status_code}")
else:
    print(f"FAILED QUERY: {response.status_code}")
