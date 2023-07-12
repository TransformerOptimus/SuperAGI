import pinecone
import openai
from qdrant_client import models, QdrantClient
import chromadb
from chromadb.config import Settings
from superagi.config.config import get_config
from sqlalchemy.orm import Session

class KnowledgeToolHelper:
    
    def __init__(self):
        self.embed_model = "text-embedding-ada-002"
    
    def pinecone_get_match_vectors(self, query, vector_db_creds, knowledge_details):
        # Initializing pinecone client
        pinecone.init(api_key=vector_db_creds.api_key, environment=vector_db_creds.environment)
        index = pinecone.Index(knowledge_details["knowledge_vector_db_index_name"])

        #embedding query
        query_res = openai.Embedding.create(
            input = [query],
            engine = self.embed_model
        )

        x_query = query_res['data'][0]['embedding']
        # get relevant contexts (including the questions)
        if knowledge_details["knowledge_vector_db_index_state"] == "MARKETPLACE":
          search_res = index.query(x_query, top_k=5, include_metadata=True,filter={
          "knowledge_name": {"$in": knowledge_details["knowledge_name"]}})
        elif knowledge_details["knowledge_vector_db_index_state"] == "CUSTOM":
          search_res = index.query(x_query, top_k=5, include_metadata=True)
        
        contexts = [item['metadata']['text'] for item in search_res['matches']]
        search_res_appended =f"\nQuery:{query}\n"
        i=0
        for context in contexts:
          search_res_appended+=str(f'\nchunk{i}:\n')
          search_res_appended+=context
          i+=1
        
        return search_res_appended
    
    def qdrant_get_match_vectors(self, query, vector_db_creds, knowledge_details):
        # Initializing qdrant client
        qdrant_client = QdrantClient(
          url=vector_db_creds.url,
          api_key=vector_db_creds.api_key,
        )
        #Embedding Query
        query_res = openai.Embedding.create(
          input=[query],
          engine=self.embed_model
        )
        x_query = query_res['data'][0]['embedding']
        try:
          if knowledge_details["knowledge_vector_db_index_state"] == "MARKETPLACE":
            search_res = qdrant_client.search(
                collection_name = knowledge_details["knowledge_vector_db_index_name"],
                query_vector = x_query,
                query_filter = models.Filter(
                  must = [
                    models.FieldCondition(
                    key = 'knoweldge_name',
                    match = models.MatchAny(any=knowledge_details["knowledge_name"])
                    )
                  ]
                ),
                limit = 5
              )
          elif knowledge_details["knowledge_vector_db_index_state"] == "CUSTOM":
            search_res = qdrant_client.search(
                collection_name = knowledge_details["knowledge_vector_db_index_name"],
                query_vector = x_query,
                limit = 5
              )
          contexts = [res.payload['text'] for res in search_res]
          search_res_appended = f"\nQuery: {query}\n"
          i = 0
          for context in contexts:
              search_res_appended += str(f"\nchunk{i}:\n")
              search_res_appended += context
              i += 1
          return search_res_appended
        
        except Exception as err:
           return f"An error occured: {str(err)}"


    