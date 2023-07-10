import openai
import google.generativeai as palm


class PalmEmbedding:
    def __init__(self, api_key, model="models/embedding-gecko-001"):
        self.model = model
        self.api_key = api_key

    def get_embedding(self, text):
        try:
            response = palm.generate_embeddings(model=self.model, text=text)
            return response['embedding']
        except Exception as exception:
            return {"error": exception}
