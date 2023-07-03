import requests

class ChromaDBClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def set_items(self, data):
        url = f"{self.base_url}/records"
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print("Record created successfully!")
        else:
            print("Failed to create record.")

    def query_by_embedding(self, query_embedding, top_k, namespace):
        url = f"{self.base_url}/records/search"
        data = {
            "query_embedding": query_embedding,
            "top_k": top_k,
            "namespace": namespace
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to retrieve matching records.")
            return None
