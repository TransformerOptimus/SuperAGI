from superagi.agent.super_agi import SuperAgi
from superagi.llms.openai import OpenAi
from superagi.tools.base_tool import FunctionalTool
from superagi.tools.file.write_file import WriteFileTool
from superagi.tools.file.read_file import ReadFileTool
from superagi.tools.google_search.tools import GoogleSearchSchema, GoogleSearchTool
from superagi.tools.google_serp_search.tools import GoogleSerpTool
from superagi.tools.twitter.send_tweet import SendTweetTool
from superagi.tools.email.read_email import ReadEmailTool
from superagi.tools.email.send_email import SendEmailTool
from superagi.tools.email.send_email_attachment import SendEmailAttachmentTool
from superagi.tools.slack.read_messages import SlackReadMessageTool
from superagi.tools.slack.send_message import SlackMessageTool
from superagi.tools.slack.tool import SlackTool
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.vector_factory import VectorFactory

memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())
# memory.add_documents([Document("Hello world")])
# memory.get_matching_text("Hello world")

def test_function(name: str):
    print("hello ramram", name)
    return

def create_campaign(campaign_name: str):
    print("create campaigns", campaign_name)
    return


tools = [
    GoogleSearchTool(),
    WriteFileTool(),
    ReadFileTool(),
    ReadEmailTool(),
    SendEmailTool(),
    SendEmailAttachmentTool(),
    SlackMessageTool(),
    SlackReadMessageTool()
    # GoogleSerpTool()
]

# result = GoogleSearchTool().execute({"query": "List down top 10 marketing strategies for a new product"})
# print(result)
# print(result.split("."))
# send_tool = SendTweetTool()
# send_tool.execute("Innovation isn't a one-time event; it's a culture. It's about daring to question the status quo, nurturing a curiosity that stretches horizons, and constantly seeking new ways to add value #Innovation #ChangeTheWorld")


# Slack Testing Tool
userid_dict = SlackTool().generate_userid_cum_name_dict()
print(userid_dict)
'''
    The ids from the above dict can be used to send and retrieve messages from groups/ individual chats
'''
result = SlackReadMessageTool().execute({"id": "C059UFQPRU5"})
print(result)
result = SlackMessageTool().execute({"id": "U059QRHRYDU", "message": "Hii!"})
print(result)


superagi = SuperAgi.from_llm_and_tools("Super AGI", "To solve any complex problems for you", memory, tools, OpenAi(model="gpt-4"))
user_goal=[]
user_goal=str(input("Enter your Goals seperated by ',':\n")).split(",")
superagi.execute(user_goal)
