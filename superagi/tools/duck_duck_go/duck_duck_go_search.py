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

#Const variables
DUCKDUCKGO_MAX_ATTEMPTS = 3
WEBPAGE_EXTRACTOR_MAX_ATTEMPTS=2
MAX_LINKS_TO_SCRAPE=3
NUM_RESULTS_TO_USE=10
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

        search_results = self.get_raw_duckduckgo_results(query)
        links=[]                                                                        
        
        for result in search_results:                                                       
            links.append(result["href"])
        
        webpages=self.get_content_from_url(links)

        results=self.get_formatted_webpages(search_results,webpages)                        #array to store objects with keys :{"title":snippet , "body":webpage content, "links":link URL}
        
        summary = self.summarise_result(query, results)                                     #summarize the content gathered using the function
        links = [result["links"] for result in results if len(result["links"]) > 0]

        if len(links) > 0:
            return summary + "\n\nLinks:\n" + "\n".join("- " + link for link in links[:3])

        return summary


    def get_formatted_webpages(self,search_results,webpages):
        """
        Generate an array of formatted webpages which can be passed to the summarizer function (summarise_result).

        Args:
            search_results : The array of objects which were fetched by DuckDuckGo.

        Returns:
            Returns the result array which is an array of objects
        """

        results=[]                                                                          #array to store objects with keys :{"title":snippet , "body":webpage content, "links":link URL}
        i = 0
        
        for webpage in webpages:
            results.append({"title": search_results[i]["title"], "body": webpage, "links": search_results[i]["href"]})
            i += 1
            if TokenCounter.count_text_tokens(json.dumps(results)) > 3000:
                break    

        return results

    def get_content_from_url(self,links):
        """
        Generates a webpage array which stores the content fetched from the links
        Args:
            links : The array of URLs which were fetched by DuckDuckGo.

        Returns:
            Returns a webpage array which stores the content fetched from the links
        """

        webpages=[]                                                                         #webpages array for storing the contents extracted from the links
        
        if links:
            for i in range(0, MAX_LINKS_TO_SCRAPE):                                         #using first 3 (Value of MAX_LINKS_TO_SCRAPE) links
                time.sleep(3)
                content = WebpageExtractor().extract_with_bs4(links[i])                     #takes in the link and returns content extracted from Webpage extractor
                max_length = len(' '.join(content.split(" ")[:500]))    
                content = content[:max_length]                                              #formatting the content
                attempts = 0
                while content == "" and attempts < WEBPAGE_EXTRACTOR_MAX_ATTEMPTS:
                    attempts += 1
                    content = WebpageExtractor().extract_with_bs4(links[i])
                    content = content[:max_length]
                webpages.append(content)

        return webpages

    def get_raw_duckduckgo_results(self,query):
        """
        Gets raw search results from the duckduckgosearch python package
        Args:
            query : The query to search for.

        Returns:
            Returns raw search results from the duckduckgosearch python package
        """
        search_results = []
        attempts = 0

        while attempts < DUCKDUCKGO_MAX_ATTEMPTS:
            if not query:                                                                   #checking if string is empty, if it is empty-> convert array to JSON object and return it;
                return json.dumps(search_results)

            results = DDGS().text(query)                                                    #text() method from DDGS takes in query (String) as input and returns the results 
            search_results = list(islice(results, NUM_RESULTS_TO_USE))                      #gets first 10 results from results and stores them in search_results
            if search_results:                                                              #if search result is populated,break as there is no need to attempt the search again
                break

            # time.sleep(1)
            attempts += 1
        
        return search_results

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
