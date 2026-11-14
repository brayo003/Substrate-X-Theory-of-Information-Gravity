import urllib.request

url = "https://opendata.cern.ch/record/303/files/DoubleMu.csv"
output = "cms_real_collisions.csv"

print(f"⚛️ V13 DATA ACQUISITION: Requesting real 7 TeV collisions...")

req = urllib.request.Request(
    url, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
)

try:
    with urllib.request.urlopen(req) as response, open(output, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print(f"✅ SUCCESS: {output} saved.")
except Exception as e:
    print(f"❌ FAILED: {e}")
