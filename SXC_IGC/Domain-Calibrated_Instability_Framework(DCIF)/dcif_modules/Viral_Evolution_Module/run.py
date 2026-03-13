import pandas as pd
from ntscraper import Nitter

# Initialize the scraper (Nitter instances are free gateways to X)
scraper = Nitter()

def check_live_twitter(query, limit=50):
    print(f"⚛️ DIRECT AUDIT: Scraping live data for {query}...")
    
    # We scrape the 'recent' stream to see the current state
    try:
        results = scraper.get_posts(query, mode='hashtag', number=limit)
    except Exception as e:
        print(f"! Connection Interrupted: {e}")
        return

    data = []
    for post in results['tweets']:
        data.append({
            'timestamp': post['date'],
            'text': post['text'],
            'stats': post['stats'],
            # We treat 'views' or 'likes' as the raw Excitation signal
            'excitation': post['stats']['views'] if post['stats']['views'] else 0
        })

    df = pd.DataFrame(data)
    # This creates the file your Viral Evolution Module needs
    df.to_csv('viral_input.csv', index=False)
    print(f"✓ {len(df)} Real-world data points saved to viral_input.csv")

# Executing for today's high-tension topics
check_live_twitter("MarketCrash", limit=25)
