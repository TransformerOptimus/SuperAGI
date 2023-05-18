from superagi.agent.super_agi import SuperAgi
from superagi.llms.openai import OpenAi
from superagi.tools.base_tool import FunctionalTool
from superagi.tools.twitter.send_tweet import SendTweetTool
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
    FunctionalTool(name="Search", description="Helps to search google", func=test_function),
    FunctionalTool(name="Campaign Create", description="Creates campaign", func=create_campaign)
]

send_tool = SendTweetTool()
send_tool.execute("Innovation isn't a one-time event; it's a culture. It's about daring to question the status quo, nurturing a curiosity that stretches horizons, and constantly seeking new ways to add value #Innovation #ChangeTheWorld")
# superagi = SuperAgi.from_llm_and_tools("Super AGI", "Super AGI", memory, tools, OpenAi())
# superagi.execute(["I want to send campaign"])