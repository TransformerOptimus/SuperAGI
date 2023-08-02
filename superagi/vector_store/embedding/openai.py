import openai


class OpenAiEmbedding:
    def __init__(self, api_key, model="text-embedding-ada-002"):
        self.model = model
        self.api_key = api_key

    def get_embedding(self, text):
        try:
            # openai.api_key = get_config("OPENAI_API_KEY")
            response = openai.Embedding.create(
                api_key=self.api_key,
                input=[text],
                engine=self.model
            )
            return response['data'][0]['embedding']
        except Exception as exception:
            return {"error": exception}
