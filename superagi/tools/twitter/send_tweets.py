from typing import Type

from pydantic import BaseModel, Field

from superagi.helper.twitter_helper import TwitterHelper
from superagi.helper.twitter_tokens import TwitterTokens
from superagi.tools.base_tool import BaseTool


class SendTweetsInput(BaseModel):
    tweet_text: str = Field(...,
                            description="Tweet text to be posted from twitter handle, if no value is given keep the default value as 'None'")
    is_media: bool = Field(..., description="'True' if there is any media to be posted with Tweet else 'False'.")
    media_files: list = Field(..., description="Name of the media files to be uploaded.")


class SendTweetsTool(BaseTool):
    name: str = "Send Tweets Tool"
    args_schema: Type[BaseModel] = SendTweetsInput
    description: str = "Send and Schedule Tweets for your Twitter Handle"
    agent_id: int = None
    agent_execution_id: int = None

    def _execute(self, is_media: bool, tweet_text: str = 'None', media_files: list = []):
        toolkit_id = self.toolkit_config.toolkit_id
        session = self.toolkit_config.session
        creds = TwitterTokens(session).get_twitter_creds(toolkit_id)
        params = {}
        if is_media:
            media_ids = TwitterHelper().get_media_ids(session, media_files, creds, self.agent_id,
                                                      self.agent_execution_id)
            params["media"] = {"media_ids": media_ids}
        if tweet_text is not None:
            params["text"] = tweet_text
        tweet_response = TwitterHelper().send_tweets(params, creds)
        if tweet_response.status_code == 201:
            return "Tweet posted successfully!!"
        else:
            return "Error posting tweet. (Status code: {})".format(tweet_response.status_code)
