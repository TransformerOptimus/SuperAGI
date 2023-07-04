import json
import requests
from typing import Type, Optional,Union
import time
from superagi.lib.logger import logger
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS
from itertools import islice
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
from superagi.helper.webpage_extractor import WebpageExtractor

DUCKDUCKGO_MAX_ATTEMPTS = 3
class DuckDuckGoSearchSchema(BaseModel):
    query: str = Field(
        ...,
        description="The search query for duckduckgo search.",
    )

class DuckDuckGoSearchTool(BaseTool):
    """
    Duck Duck Go Search tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "DuckDuckGoSearch"
    description = (
        "A tool for performing a DuckDuckGo search and extracting snippets and webpages."
        "Input should be a search query."
    )
    args_schema: Type[DuckDuckGoSearchSchema] = DuckDuckGoSearchSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, query: str) -> tuple:
        
        """
        Execute the DuckDuckGo search tool.

        Args:
            query : The query to search for.

        Returns:
            Search result summary along with related links
        """

        search_results = []
        attempts = 0

        while attempts < DUCKDUCKGO_MAX_ATTEMPTS:
            if not query:                                                                   #checking if string is empty, if it is empty-> convert array to JSON object and return it;
                return json.dumps(search_results)

            results = DDGS().text(query)                                                    #text() method from DDGS takes in query (String) as input and returns the results 
            search_results = list(islice(results, 10))                                      #gets first 10 results from results and stores them in search_results
            if search_results:                                                              #if search result is populated,break as there is no need to attempt the search again
                break

            time.sleep(1)
            attempts += 1

        links=[]                                                                            #array for storing all the links generated
        info=[]                                                                             #array for storing all the information generated
        snippets=[]                                                                         #array for storing all the snippets/titles generated

        for result in search_results:                                                       #populating the 3 arrays,Each item of the search_result array is an object with keys->"title","href","body"
            snippets.append(result["title"])  
            links.append(result["href"])
            info.append(result["body"])

        webpages=[]                                                                         #webpages array for storing the contents extracted from the links
        
        if links:
            for i in range(0, 3):                                                           #using first 3 links
                time.sleep(3)
                content = WebpageExtractor().extract_with_bs4(links[i])                     #takes in the link and returns content extracted from Webpage extractor
                max_length = len(' '.join(content.split(" ")[:500]))    
                content = content[:max_length]                                              #formating the content
                attempts = 0
                while content == "" and attempts < 2:
                    attempts += 1
                    content = WebpageExtractor().extract_with_bs4(links[i])
                    content = content[:max_length]
                webpages.append(content)

        results=[]                                                                          #array to store objects with keys :{"title":snippet , "body":webpage content, "links":link URL}
        i = 0
        for webpage in webpages:
            results.append({"title": snippets[i], "body": webpage, "links": links[i]})
            i += 1
            if TokenCounter.count_text_tokens(json.dumps(results)) > 3000:
                break       

        summary = self.summarise_result(query, results)                                     #summarize the content gathered using the function
        links = [result["links"] for result in results if len(result["links"]) > 0]
        if len(links) > 0:
            return summary + "\n\nLinks:\n" + "\n".join("- " + link for link in links[:3])
        return summary



    def summarise_result(self, query, snippets):
        """
        Summarise the result of a DuckDuckGo search.

        Args:
            query : The query to search for.
            snippets (list): A list of snippets from the search.

        Returns:
            A summary of the search result.
        """
        summarize_prompt ="""Summarize the following text `{snippets}`
            Write a concise or as descriptive as necessary and attempt to
            answer the query: `{query}` as best as possible. Use markdown formatting for
            longer responses."""

        summarize_prompt = summarize_prompt.replace("{snippets}", str(snippets))
        summarize_prompt = summarize_prompt.replace("{query}", query)

        messages = [{"role": "system", "content": summarize_prompt}]
        result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
        return result["content"]
