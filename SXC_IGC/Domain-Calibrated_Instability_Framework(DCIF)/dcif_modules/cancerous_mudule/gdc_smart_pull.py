import requests
import os

def download_filtered_data(manifest_path):
    with open(manifest_path, 'r') as f:
        lines = f.readlines()[1:] 

    if not os.path.exists('raw_data'): os.makedirs('raw_data')
    
    for line in lines:
        parts = line.split('\t')
        file_id, file_name = parts[0], parts[1]
        file_size = int(parts[2])

        # Logic Gate: Skip massive BAM files, prioritize quantification and segments
        if file_size > 500_000_000: 
            print(f"SKIPPING: {file_name} (Too large for rapid trace)")
            continue
            
        print(f"PULLING: {file_name}...")
        url = f"https://api.gdc.cancer.gov/data/{file_id}"
        
        try:
            r = requests.get(url, stream=True, timeout=30)
            if r.status_code == 200:
                with open(f"raw_data/{file_name}", 'wb') as f_out:
                    for chunk in r.iter_content(chunk_size=8192):
                        f_out.write(chunk)
                print(f"SUCCESS: {file_name}")
            else:
                print(f"DENIED: {file_id} (Access Restricted)")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    download_filtered_data('portal_manifest.tsv')
