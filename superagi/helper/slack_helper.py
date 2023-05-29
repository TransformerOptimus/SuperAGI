from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackHelper:
    def __init__(self, slack_bot_token):
        self.slack_bot_token= slack_bot_token
        self.client = WebClient(token=self.slack_bot_token)

    def get_unread_messages(self, channel_id):
        try:
            response = self.client.conversations_history(
                channel=channel_id,
                oldest=self.get_last_read_timestamp(channel_id),
            )
            return response["messages"]
        except SlackApiError as e:
            print(f"Error getting unread messages: {e}")
            return []

    def get_last_read_timestamp(self, channel_id):
        try:
            response = self.client.conversations_info(channel=channel_id)
            return response["channel"]["last_read"]
        except SlackApiError as e:
            print(f"Error getting last read timestamp: {e}")
            return 0

    def get_channels(self):
        try:
            response = self.client.conversations_list()
            return response["channels"]
        except SlackApiError as e:
            print(f"Error getting channels: {e}")
            return []
