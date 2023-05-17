import os

import openai


class OpenAiEmbedding:
    def __init__(self, model="text-embedding-ada-002"):
        self.model = model

    async def get_embedding_async(self, text):
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = await openai.Embedding.create(
                input=[text],
                engine=self.model
            )
            return response['data'][0]['embedding']
        except Exception as exception:
            return {"error": exception}

    def get_embedding(self, text):
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.Embedding.create(
                input=[text],
                engine=self.model
            )
            return response['data'][0]['embedding']
        except Exception as exception:
            return {"error": exception}
