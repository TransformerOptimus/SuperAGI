import tweepy

consumer_key = 'CqvH70BYH9bdbT5gvY007G8gI'
consumer_secret = '4XGqg5DRJYIxdVmR9qi9ISebf2JzILuHSHqlenFAcqitDatafx'
access_token = '1659075724479991808-hYGgKg5I9nkCn1kvLdIoHs3OSGtdFt'
access_token_secret = 'TR7vyuMOF7EZkiH1dF0ZRlgG21Ftm202aSQr2oGaLgK6x'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create API object
api = tweepy.API(auth)

# Verify credentials and get user information

tweet_text = "Hello, Twitter! This is my first tweet using Tweepy!"
api.update_status(tweet_text)

# Print success message
print("Tweet sent successfully!")
