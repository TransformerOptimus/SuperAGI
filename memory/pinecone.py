# build a pinecone wrapper
from memory.embedding.openai import OpenAiEmbedding
import pinecone


class Pinecone:
  def __init__(self, search_index_name: str = "long_term_memory"):
    self.embed_model = OpenAiEmbedding(model="text-embedding-ada-002")
    self.search_index_name = "long_term_memory"

  async def get_match(self, query):
    namespace = "long_term_memory"

    embed_text = await self.embed_model.get_embedding(query)

    index = pinecone.Index(self.search_index_name)
    # get relevant contexts (including the questions)
    res = index.query(embed_text, top_k=5, namespace=namespace, include_metadata=True)

    contexts = [item['metadata']['text'] for item in res['matches']]
    return contexts
