from superagi.config.config import get_config
from superagi.tools.base_tool import BaseTool

from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError


class SlackTool(BaseTool):
    @classmethod
    def build_slack_web_client(cls):
        slack_bot_token = get_config("SLACK_BOT_TOKEN")
        return WebClient(token=slack_bot_token)

# client = WebClient(token="xoxb-5337483602338-5350192420641-9qwBk4R9t7EdpaarhhxOTckk")
# print(type(client))
# # client.chat_postMessage(channel="#general", text="Hello world!")

# response = client.conversations_list()

# # Check if the request was successful
# if response['ok']:
#     channels = response['channels']
#     for channel in channels:
#         channel_id = channel['id']
#         channel_name = channel['name']
#         print(f'Channel Name: {channel_name}, Channel ID: {channel_id}')
# else:
#     print('Failed to retrieve channel list.')


# # Replace 'CHANNEL_ID' with the ID of the channel you want to read messages from
# response = client.conversations_history(channel='C059UFQPRU5')

# # Check if the request was successful
# if response['ok']:
#     messages = response['messages']
#     for message in messages:
#         # Extract relevant information from the message
#         user = message.get('user', '')
#         text = message.get('text', '')
#         ts = message.get('ts', '')
#         print(f'{user}: {text} ({ts})')
# else:
#     print('Failed to retrieve message history.')