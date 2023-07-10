import pinecone
import openai
from qdrant_client import models, QdrantClient
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from superagi.config.config import get_config


class Knowledgetoolhelper:
  def __init__(self,openai_api_key,knowledge_api_key,knowledge_index_or_collection,knowledge_url,knowledge_environment):
    self.openai_api_key = openai_api_key
    self.knowledge_api_key = knowledge_api_key
    self.knowledge_index_or_collection = knowledge_index_or_collection
    self.knowledge_url = knowledge_url
    self.knowledge_environment = knowledge_environment
    
  
  def pinecone_get_match_vectors(self, query):
    embed_model = "text-embedding-ada-002"
    namespace = ""
    # Initializing pinecone client
    pinecone.init(api_key=self.knowledge_api_key, environment=self.knowledge_environment)
    index = pinecone.Index(self.knowledge_index_or_collection)
    #Embedding Query
    query_res = openai.Embedding.create(
      input=[query],
      engine=embed_model
    )
    x_query = query_res['data'][0]['embedding']
    
    # get relevant contexts (including the questions)
    search_res = index.query(x_query, top_k=5, include_metadata=True)#, include_values=True)
    print(search_res)
    contexts = [item['metadata']['text'] for item in search_res['matches']]
    search_res_appended=''
    search_res_appended+=f"\nQuery:{query}\n"
    i=0
    for context in contexts:
      search_res_appended+=str(f'\nchuck{i}:\n')
      search_res_appended+=context
      i+=1
      #print(search_res_appended)

    return search_res_appended

  def qdrant_get_match_vectors(self, query):
    embed_model = "text-embedding-ada-002"
    
    # Initializing qdrant client
    qdrant_client = QdrantClient(
        url=self.knowledge_url, 
        api_key=self.knowledge_api_key,
    )
    
    try:
        search_res = qdrant_client.search(
            collection_name=self.knowledge_index_or_collection,
            query_vector=embed_model.encode(query).tolist(),
            limit=5
        )
     
        contexts = [res.payload['text'] for res in search_res]
        print('4')  
        search_res_appended = ''
        search_res_appended += f"\nQuery: {query}\n"
        i = 0
        for context in contexts:
            search_res_appended += str(f'\nchunk{i}:\n')
            search_res_appended += context
            i += 1

        return search_res_appended
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Handle the exception or raise it again if needed

  def chroma_get_match_vectors(self, query):
    embed_model = SentenceTransformer('all-mpnet-base-v2')
    encoder = SentenceTransformer('all-MiniLM-L6-v2')  # Model to create embeddings
    
    # Initializing qdrant client
    chroma_client=chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",
                                           persist_directory="workspace/Memoryfolder"
                                    #persist_directory="/Users/adityarajsingh/Documents/Autonomous/Chroma/Memoryfolder"
                                  ))
    
    collection = chroma_client.get_collection(name=self.knowledge_index_or_collection)
    x_query=encoder.encode(query).tolist()
    #Query the collection 
    search_res = collection.query(
    query_embeddings=x_query,
    n_results=5
    #where={"metadata_field": "is_equal_to_this"},
    #where_document={"$contains":"search_string"}
    )
    
    contexts=search_res['documents']

    search_res_appended = ''
    search_res_appended += f"\nQuery: {query}\n"
    i = 0
    for context in contexts:
      for context_text in context:
        search_res_appended += str(f'\nchunk{i}:\n')
        search_res_appended += context_text
        i += 1

    return search_res_appended  
