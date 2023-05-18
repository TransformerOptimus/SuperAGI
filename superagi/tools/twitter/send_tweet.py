import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool

import tweepy

class SentTweetSchema(BaseModel):
    tweet_text: str = Field(
        ...,
        description="Text post you want to write on twitter.",
    )


class SendTweetTool(BaseTool):
    name = "SendTweet"
    description = (
        "A wrapper around Twitter. "
        "Useful to send/write tweet on twitter "
        "Input should be a search query."
    )
    args_schema: Type[SentTweetSchema] = SentTweetSchema

    def execute(self, tweet_text: str):
        consumer_key = os.environ.get("TW_CONSUMER_KEY")
        consumer_secret = os.environ.get("TW_CONSUMER_SECRET")
        access_token = os.environ.get("TW_ACCESS_TOKEN")
        access_token_secret = os.environ.get("TW_ACCESS_TOKEN_SECRET")
        bearer_token = os.environ.get("TW_BEARER_SECRET")
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        try:
            api = tweepy.API(auth)
            api.update_status(tweet_text)
            # response = client.create_tweet(text=tweet_text, user_auth=False)
            # print(response)
            return "Tweet sent successfully!"
        except tweepy.TweepyException as e:
            print(e)
            return f"Error sending tweet: {e}"
