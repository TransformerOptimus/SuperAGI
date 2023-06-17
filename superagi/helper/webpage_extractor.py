from io import BytesIO
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfReader
import requests
import re
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException, Config
from requests_html import HTMLSession
import time
import random
from lxml import html
from superagi.lib.logger import logger

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
]

class WebpageExtractor:

    def __init__(self, num_extracts=3):
        """
        Initialize the WebpageExtractor class.
        """
        self.num_extracts = num_extracts

    def extract_with_3k(self, url):
        """
        Extract the text from a webpage using the 3k method.

        Args:
            url (str): The URL of the webpage to extract from.

        Returns:
            str: The extracted text.
        """
        try:
            if url.lower().endswith(".pdf"):
                response = requests.get(url)
                response.raise_for_status()

                with BytesIO(response.content) as pdf_data:
                    reader = PdfReader(pdf_data)
                    content = " ".join([reader.getPage(i).extract_text() for i in range(reader.getNumPages())])

            else:
                config = Config()
                config.browser_user_agent = random.choice(USER_AGENTS)
                config.request_timeout = 10
                session = HTMLSession()

                response = session.get(url)
                response.html.render(timeout=config.request_timeout)
                html_content = response.html.html

                article = Article(url, config=config)
                article.set_html(html_content)
                article.parse()
                content = article.text.replace('\t', ' ').replace('\n', ' ').strip()

            return content[:1500]

        except ArticleException as ae:
            logger.error(f"Error while extracting text from HTML (newspaper3k): {str(ae)}")
            return f"Error while extracting text from HTML (newspaper3k): {str(ae)}"

        except RequestException as re:
            logger.error(f"Error while making the request to the URL (newspaper3k): {str(re)}")
            return f"Error while making the request to the URL (newspaper3k): {str(re)}"

        except Exception as e:
            logger.error(f"Unknown error while extracting text from HTML (newspaper3k): {str(e)}")
            return ""

    def extract_with_bs4(self, url):
        """
        Extract the text from a webpage using the BeautifulSoup4 method.

        Args:
            url (str): The URL of the webpage to extract from.

        Returns:
            str: The extracted text.
        """
        headers = {
            "User-Agent": random.choice(USER_AGENTS)
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for tag in soup(['script', 'style', 'nav', 'footer', 'head', 'link', 'meta', 'noscript']):
                    tag.decompose()

                main_content_areas = soup.find_all(['main', 'article', 'section', 'div'])
                if main_content_areas:
                    main_content = max(main_content_areas, key=lambda x: len(x.text))
                    content_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
                    content = ' '.join([tag.text.strip() for tag in main_content.find_all(content_tags)])
                else:
                    content = ' '.join([tag.text.strip() for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])

                content = re.sub(r'\t', ' ', content)
                content = re.sub(r'\s+', ' ', content)
                return content
            elif response.status_code == 404:
                return f"Error: 404. Url is invalid or does not exist. Try with valid url..."
            else:
                logger.error(f"Error while extracting text from HTML (bs4): {response.status_code}")
                return f"Error while extracting text from HTML (bs4): {response.status_code}"

        except Exception as e:
            logger.error(f"Unknown error while extracting text from HTML (bs4): {str(e)}")
            return ""

    def extract_with_lxml(self, url):
        """
        Extract the text from a webpage using the lxml method.

        Args:
            url (str): The URL of the webpage to extract from.

        Returns:
            str: The extracted text.
        """
        try:
            config = Config()
            config.browser_user_agent = random.choice(USER_AGENTS)
            config.request_timeout = 10
            session = HTMLSession()

            response = session.get(url)
            response.html.render(timeout=config.request_timeout)
            html_content = response.html.html

            tree = html.fromstring(html_content)
            paragraphs = tree.cssselect('p, h1, h2, h3, h4, h5, h6')
            content = ' '.join([para.text_content() for para in paragraphs if para.text_content()])
            content = content.replace('\t', ' ').replace('\n', ' ').strip()

            return content

        except ArticleException as ae:
            logger.error("Error while extracting text from HTML (lxml): {str(ae)}")
            return ""

        except RequestException as re:
            logger.error(f"Error while making the request to the URL (lxml): {str(re)}")
            return ""

        except Exception as e:
            logger.error(f"Unknown error while extracting text from HTML (lxml): {str(e)}")
            return ""
    