import random
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel
from superagi.lib.logger import logger
import time

# Fallback hosts if API fails or instances are unavailable
FALLBACK_SEARX_HOSTS = ["https://search.ononoki.org", "https://searx.be", "https://search.us.projectsegfau.lt"]
SEARX_INSTANCES_API = "https://searx.space/data/instances.json"

# Cache for instances list
_instances_cache: Optional[List[str]] = None
_cache_timestamp: float = 0
CACHE_DURATION = 3600  # Cache for 1 hour

class SearchResult(BaseModel):
    """
    Represents a single search result from Searx

    Attributes:
        id : The ID of the search result.
        title : The title of the search result.
        link : The link of the search result.
        description : The description of the search result.
        sources : The sources of the search result.
    """
    id: int
    title: str
    link: str
    description: str
    sources: List[str]

    def __str__(self):
        return f"""{self.id}. {self.title} - {self.link} 
{self.description}"""

def get_searx_instances() -> List[str]:
    """
    Fetches available SearX instances from searx.space API.
    Falls back to hardcoded hosts if API is unavailable.

    Returns:
        List of available SearX instance URLs.
    """
    global _instances_cache, _cache_timestamp
    
    # Return cached instances if still valid
    current_time = time.time()
    if _instances_cache is not None and (current_time - _cache_timestamp) < CACHE_DURATION:
        return _instances_cache
    
    try:
        response = httpx.get(SEARX_INSTANCES_API, timeout=5.0)
        if response.status_code == 200:
            instances_data = response.json()
            instances = []
            
            # Extract instance URLs from the API response
            # The API returns a dictionary with "instances" key containing instance data
            instances_dict = instances_data.get("instances", {})
            
            for instance_url, instance_info in instances_dict.items():
                # Filter for instances that are online
                if isinstance(instance_info, dict):
                    status = instance_info.get("status", "")
                    # Accept instances with status "up" or "ok"
                    if status in ["up", "ok"]:
                        # Ensure URL has https:// prefix if missing
                        if not instance_url.startswith("http"):
                            instance_url = "https://" + instance_url
                        elif instance_url.startswith("http://"):
                            # Prefer HTTPS over HTTP
                            instance_url = instance_url.replace("http://", "https://", 1)
                        instances.append(instance_url)
                elif isinstance(instance_info, str):
                    # Some instances might just be URLs as strings
                    if instance_info.startswith("http"):
                        instances.append(instance_info)
            
            if instances:
                _instances_cache = instances
                _cache_timestamp = current_time
                logger.info(f"Fetched {len(instances)} SearX instances from API")
                return instances
            else:
                logger.warning("No available instances found in API response, using fallback hosts")
        else:
            logger.warning(f"Failed to fetch instances: HTTP {response.status_code}")
    except httpx.TimeoutException:
        logger.warning("Timeout fetching SearX instances from API, using fallback hosts")
    except httpx.RequestError as e:
        logger.warning(f"Network error fetching SearX instances: {e}, using fallback hosts")
    except Exception as e:
        logger.warning(f"Error fetching SearX instances from API: {e}, using fallback hosts")
    
    # Fallback to hardcoded hosts
    return FALLBACK_SEARX_HOSTS


def search(query):
    """
    Gets the raw HTML of a searx search result page

    Args:
        query : The query to search for.
        
    Returns:
        Raw HTML of the search result page.
        
    Raises:
        Exception: If the SearX instance returns a non-200 status code.
    """
    instances = get_searx_instances()
    searx_url = random.choice(instances)
    
    res = httpx.get(
        searx_url + "/search", 
        params={"q": query}, 
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/114.0"},
        timeout=10.0
    )
    if res.status_code != 200:
        logger.info(f"Searx returned {res.status_code} status code for {searx_url}")
        raise Exception(f"Searx returned {res.status_code} status code")

    return res.text

def clean_whitespace(s: str):
    """
    Cleans up whitespace in a string

    Args:
        s : The string to clean up.

    Returns:
        The cleaned up string.
    """
    return " ".join(s.split())


def scrape_results(html):
    """
    Converts raw HTML into a list of SearchResult objects

    Args:
        html : The raw HTML to convert.

    Returns:
        A list of SearchResult objects.
    """
    soup = BeautifulSoup(html, "html.parser")
    result_divs = soup.find_all(attrs={"class": "result"})
    
    result_list = []
    n = 1
    for result_div in result_divs:
        if result_div is None:
            continue
        # Needed to work on multiple versions of Searx
        header = result_div.find(["h4", "h3"])
        if header is None:
            continue
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
