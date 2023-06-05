# from playwright.sync_api import sync_playwright
# from superagi.tools.base_tool import BaseTool
# from pydantic import BaseModel


# # class StartBrowserSchema(BaseModel):
# #     pass


# # class StartBrowserTool(BaseTool):
# #     name = "Start Browser"
# #     description = "A tool to start the Playwright browser.Starts the browser for web interaction. Must be ran before attempting to perform any other web interaction plugins"
# #     args_schema = StartBrowserSchema

# #     def _execute(self) -> str:
# #         global browser
# #         global page

# #         browser = (
# #             sync_playwright()
# #             .start()
# #             .chromium.launch(
# #                 headless=False,
# #             )
# #         )
# #         page = browser.new_page()
# #         page.set_viewport_size({"width": 1280, "height": 1080})

# #         return "Browser successfully started!"


# from pydantic import BaseModel, Field
# from superagi.tools.base_tool import BaseTool

# class StartBrowserAndGoToPageSchema(BaseModel):
#     url: str = Field(..., description="The URL to navigate to.")

# class StartBrowserAndGoToPageTool(BaseTool):
#     name = "Start Browser and Go to Page"
#     description = "A tool to start the Playwright browser and navigate to a specific URL.Must be ran before attempting to perform any other web interaction plugins"
#     args_schema = StartBrowserAndGoToPageSchema

#     def _execute(self, url: str) -> str:
#         global browser
#         global page
#         global client
#         global page_element_buffer

#         browser = (
#             sync_playwright()
#             .start()
#             .chromium.launch(
#                 headless=False,
#             )
#         )

#         page = browser.new_page()
#         page.set_viewport_size({"width": 1280, "height": 1080})

#         try:
#             page.goto(url=url if "://" in url else "http://" + url)
#             client = page.context.new_cdp_session(page)
#             page_element_buffer = {}
#         except:
#             return "Failed to go to URL, please try again and make sure the URL is correct."

#         return f"Browser successfully started and navigated to {url}!"


# from playwright.sync_api import sync_playwright
# from superagi.tools.base_tool import BaseTool
# from pydantic import BaseModel, Field

# # Declare the 'page' variable as a global variable at the top of the file
# page = None
# page_element_buffer = None
# client = None

# class StartBrowserAndGoToPageSchema(BaseModel):
#     url: str = Field(..., description="The URL to navigate to.")

# class StartBrowserAndGoToPageTool(BaseTool):
#     name = "Start Browser and Go to Page"
#     description = "A tool to start the Playwright browser and navigate to a specific URL.Must be ran before attempting to perform any other web interaction plugins"
#     args_schema = StartBrowserAndGoToPageSchema

#     def _execute(self, url: str) -> str:
#         global browser
#         global client
#         global page_element_buffer

#         browser = (
#             sync_playwright()
#             .start()
#             .chromium.launch(
#                 headless=False,
#             )
#         )

#         # Remove the 'global page' statement and directly set the 'page' variable
#         page = browser.new_page()
#         page.set_viewport_size({"width": 1280, "height": 1080})

#         try:
#             page.goto(url=url if "://" in url else "http://" + url)
#             client = page.context.new_cdp_session(page)
#             page_element_buffer = {}
#         except:
#             return "Failed to go to URL, please try again and make sure the URL is correct."

#         return f"Browser successfully started and navigated to {url}!"

from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from superagi.helper.browser_wrapper import browser_wrapper

class StartBrowserAndGoToPageSchema(BaseModel):
    url: str = Field(..., description="The URL to navigate to.The format is 'url': <url>")

class StartBrowserAndGoToPageTool(BaseTool):
    name = "Start Browser and Go to Page"
    description = "A tool to start the Playwright browser.Opening ClassyDevelopers"

    args_schema = StartBrowserAndGoToPageSchema

    def _execute(self, url: str) -> str:
        return browser_wrapper.start_browser_and_goto_page(url)