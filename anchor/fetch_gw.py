from gwosc.locate import get_event_urls

try:
    urls = get_event_urls('GW150914', detector='H1', sample_rate=4096)
    if urls:
        print(f"\n[SUCCESS] Substrate X Cosmic Layer Found.")
        print(f"Download the real strain data here:\n{urls[0]}")
    else:
        print("No URLs found for this event.")
except Exception as e:
    print(f"Error: {e}")
