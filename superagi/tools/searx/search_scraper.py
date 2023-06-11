import urllib.request
import json
import operator
from typing import List
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel

def getSearxHost():
    with urllib.request.urlopen("https://searx.space/data/instances.json") as url:
        data = json.load(url)
        instancelist = data["instances"]
        valid_instances = {}

        for key, value in instancelist.items():
            if value["network_type"] == "normal" and value["http"]["error"] is None:
                try:
                    valid_instances[key] = value["timing"]["initial"]["all"]["value"] + value["timing"]["search_go"]["all"]["median"] + value["timing"]["search"]["all"]["median"]
                except KeyError:
                    pass
    
        sorted_instances = dict(sorted(valid_instances.items(), key=operator.itemgetter(1)))
        return sorted_instances

class SearchResult(BaseModel):
    id: int
    title: str
    link: str
    description: str
    sources: List[str]

    def __str__(self):
        return f"""{self.id}. {self.title} - {self.link} 
{self.description}"""

def search(query):
    '''Gets the raw HTML of a searx search result page'''
    searx_urls = getSearxHost()
    for searx_url in searx_urls:
        res = httpx.get(
            searx_url + "/search", params={"q": query}, headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/114.0"}
        )
        if res.status_code != 200:
            pass
        else:
            return res.text
    raise Exception(f"All Searx instances doesn't returned 200")

def clean_whitespace(s: str):
    return " ".join(s.split())


def scrape_results(html):
    '''Converts raw HTML into a list of SearchResult objects'''
    soup = BeautifulSoup(html, "html.parser")
    result_divs = soup.find_all(attrs={"class": "result"})
    
    result_list = []
    n = 1
    for result_div in result_divs:
        # Needed to work on multiple versions of Searx
        header = result_div.find(["h4", "h3"])
        link = header.find("a")["href"]
        title = header.text.strip()

        description = clean_whitespace(result_div.find("p").text)

        # Needed to work on multiple versions of Searx
        sources_container = result_div.find(
            attrs={"class": "pull-right"}
        ) or result_div.find(attrs={"class": "engines"}) 
        source_spans = sources_container.find_all("span")
        sources = []
        for s in source_spans:
            sources.append(s.text.strip())

        result = SearchResult(
            id=n, title=title, link=link, description=description, sources=sources
        )
        result_list.append(result)
        n += 1

    return result_list


def search_results(query):
    '''Returns a text summary of the search results via the SearchResult.__str__ method'''
    return "\n\n".join(list(map(lambda x: str(x), scrape_results(search(query)))))
