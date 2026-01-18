import requests
import json

def get_normal_miRNA_manifest():
    filters = {
        "op": "and",
        "content": [
            {"op": "in", "content": {"field": "cases.project.project_id", "value": ["TCGA-LUAD"]}},
            {"op": "in", "content": {"field": "files.data_type", "value": ["miRNA Expression Quantification"]}},
            {"op": "in", "content": {"field": "samples.sample_type", "value": ["Solid Tissue Normal"]}}
        ]
    }
    
    params = {
        "filters": json.dumps(filters),
        "fields": "file_id,file_name,file_size",
        "format": "TSV",
        "size": "5"
    }

    response = requests.get("https://api.gdc.cancer.gov/files", params=params)
    if response.status_code == 200:
        with open("normal_miRNA_manifest.txt", "w") as f:
            f.write(response.text)
        print("SUCCESS: normal_miRNA_manifest.txt created.")
    else:
        print(f"FAILED: {response.status_code}")

if __name__ == "__main__":
    get_normal_miRNA_manifest()
