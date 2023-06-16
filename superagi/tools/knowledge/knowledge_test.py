import json
from abc import ABC, abstractmethod
from superagi.config.config import get_config
import openai

from typing import Type, List
from pydantic import BaseModel, Field

from superagi.helper.knowledge_tool import Knowledgetoolhelper
from superagi.tools.base_tool import BaseTool
# from superagi.tools.file.read_file import ReadFileTool
import pandas as pd

# 1. define input schema
class KnowledgeSearchSchema(BaseModel):
    query: str = Field(..., description="The search query for knowledge store search")

# 2. setup name, arg, description
class KnowledgeSearchTool(BaseTool):
    name: str = "Knowledge Search"
    args_schema: Type[BaseModel] = KnowledgeSearchSchema
    description = (
        "A tool for performing a Knowledge search."
        "Input should be a search query."
    )

    def _execute(self, query: str):
        print(query)
        query_knowledge = Knowledgetoolhelper()
        req_context = query_knowledge.get_match_vectors(query)
        return req_context

        
        
        
        #messages = []
        # message is system message
        #return ("Embed tool results")






















# class EmbeddingsCreatorSchema(BaseModel):
#     file_name: str = Field(...,description="The text file to be converted into embeddings.")

# class EmbeddingsCreatorTool(BaseTool):
#   name = "Knowledge"
#   args_schema: Type[BaseModel] = EmbeddingsCreatorSchema
#   description = (
#         "A tool for reading text from a text file and then transforming text into semantic vectors or embeddings. "
#         "Input should be a text file."
#   )
  
#   def _execute(self, file_name: str):
#         # model = "text-embedding-ada-002"'
#         # print(type(file_name))
#         # print(file_name,'daedhafjeh')
#         file_content = ReadFileTool().execute(file_name)
#         # file_content = "hdfskjdfhksjh"
#         create_embeddings = Embedding_creator_tool()
#         embeddings = pd.DataFrame(create_embeddings.get_embeddings(file_content))
#         # embeddings = "sjkdfhdjsk"
#         return embeddings
 
