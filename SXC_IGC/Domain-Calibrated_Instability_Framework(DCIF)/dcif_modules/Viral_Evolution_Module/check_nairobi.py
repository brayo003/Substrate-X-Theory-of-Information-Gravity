import asyncio
from twscrape import API, gather

async def main():
    api = API()
    
    # Adding a dummy account is required by twscrape to mimic a browser
    # You can use any burner account or skip if you already have one configured
    
    query = "Nairobi #HSBCSVNS OR #Sifuna"
    print(f"⚛️ DATA HARVEST: Querying {query}...")
    
    tweets = []
    async for tweet in api.search(query, limit=20):
        tweets.append({
            'id': tweet.id,
            'text': tweet.rawContent,
            'retweets': tweet.retweetCount,
            'likes': tweet.likeCount,
            'views': tweet.viewCount
        })
        print(f"Captured: {tweet.rawContent[:50]}...")

    import pandas as pd
    df = pd.DataFrame(tweets)
    df.to_csv('viral_input.csv', index=False)
    print(f"\n✓ SUCCESS: {len(df)} units of reality saved to viral_input.csv")

if __name__ == "__main__":
    asyncio.run(main())
