from superagi.agent.super_agi import SuperAgi
from superagi.llms.openai import OpenAi
from superagi.tools.base_tool import Tool
from superagi.vector_store.document import Document
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.vector_factory import VectorFactory

memory = VectorFactory.get_vector_storage("PineCone", "super-agent-index1", OpenAiEmbedding())
memory.add_documents([Document("Hello world")])
memory.get_matching_text("Hello world")

def test_function(name: str):
    print("hello ramram", name)
    return

def create_campaign(campaign_name: str):
    print("create campaigns", campaign_name)
    return


tools = [
    Tool(name="Search", description="Helps to search google", func=test_function),
    Tool(name="Campaign Create", description="Creates campaign", func=create_campaign),
]

superagi = SuperAgi.from_llm_and_tools("Super AGI", "Super AGI", memory, tools, OpenAi())
superagi.execute(["I want to send campaign"])