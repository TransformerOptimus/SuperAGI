from superagi.agent.super_agi import SuperAgi
from superagi.llms.openai import OpenAi
from superagi.tools.base_tool import FunctionalTool
from superagi.tools.file.write_file import WriteFileTool
from superagi.tools.google_search.tools import GoogleSearchSchema, GoogleSearchTool
from superagi.tools.google_serp_search.tools import GoogleSerpTool
from superagi.tools.twitter.send_tweet import SendTweetTool
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.vector_factory import VectorFactory

memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())
tools = [
    GoogleSearchTool(),
    WriteFileTool(),
    # GoogleSerpTool()
]

superagi = SuperAgi.from_llm_and_tools("Super AGI", "To solve any complex problems for you", memory, tools, OpenAi(model="gpt-4"))
user_goal=[]
user_goal=str(input("Enter your Goals seperated by ',':\n")).split(",")
superagi.execute(user_goal)
