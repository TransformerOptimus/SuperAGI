




def get_search_index(self):
    embed_model = "text-embedding-ada-002"
    index_name = PineconeSearchModel.search_index_name
    pinecone.init(api_key="b5023255-b521-4ba6-aefc-f55d65f5a59b", enviroment="us-east-1-aws")
    if index_name not in pinecone.list_indexes():
      openai.api_key = os.getenv("OPENAI_API_KEY")
      res = openai.Embedding.create(
        input=[
          "Sample document text goes here",
          "there will be several phrases in each batch"
        ], engine=embed_model
      )

      # if does not exist, create index
      pinecone.create_index(
        index_name,
        dimension=len(res['data'][0]['embedding']),
        metric='dotproduct'
      )
    # # connect to index
    index = pinecone.Index(index_name)
    return index

  
  def get_match(self, query):
    embed_model = "text-embedding-ada-002"
    namespace = "SEO Success"
    index = pinecone.Index(self.search_index_name)
    openai.api_key = os.getenv("OPENAI_API_KEY")
    t1_start = perf_counter()
    res = openai.Embedding.create(
      input=[query],
      engine=embed_model
    )
    t1_stop = perf_counter()
    print("OpenAI Elapsed time:", t1_stop - t1_start)
    # retrieve from Pinecone
    xq = res['data'][0]['embedding']
    # get relevant contexts (including the questions)
    res = index.query(xq, top_k=5, namespace=namespace, include_metadata=True)
    t1_stop2 = perf_counter()
    print("Pinecone Elapsed time:", t1_stop2 - t1_stop)

    contexts = [item['metadata']['text'] for item in res['matches']]
    return contexts
