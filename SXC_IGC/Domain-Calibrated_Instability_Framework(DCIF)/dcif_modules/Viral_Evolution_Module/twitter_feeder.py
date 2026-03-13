import tweepy
import pandas as pd
import json

# Your Substrate-X Keys (Get these from developer.x.com)
BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"

client = tweepy.Client(bearer_token=BEARER_TOKEN)

def harvest_tweets(query, count=100):
    print(f"⚛️ Auditing Substrate for: {query}...")
    # Fetching tweets with location and language data
    tweets = client.search_recent_tweets(
        query=query, 
        max_results=count,
        tweet_fields=['created_at', 'lang', 'public_metrics'],
        expansions=['geo.place_id']
    )
    
    data = []
    if tweets.data:
        for tweet in tweets.data:
            data.append({
                'timestamp': tweet.created_at,
                'text': tweet.text,
                'lang': tweet.lang,
                'retweets': tweet.public_metrics['retweet_count'],
                'gravity_score': tweet.public_metrics['impression_count'] # Direct Info Gravity
            })
    
    df = pd.DataFrame(data)
    # Save for your Calibrate module to digest
    df.to_csv('viral_input.csv', index=False)
    print(f"✓ Harvest Complete. {len(df)} units of info saved to viral_input.csv")

# Test it with a high-tension keyword
harvest_tweets("#MarketCrash OR #AI", count=50)
