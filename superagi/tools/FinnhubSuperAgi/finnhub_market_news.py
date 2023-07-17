from finnhub import Client
from pydantic import BaseModel, Field
from typing import Type, Optional
from superagi.tools.base_tool import BaseTool

class FinnhubMarketNewsInput(BaseModel):
    category: str = Field(..., description="Get news for this market category: (general), forex, crypto")
    min_id: int = Field(..., description="Get news only after this ID")

class FinnhubMarketNewsTool(BaseTool):
    name: str = "Finnhub Market News Tool"
    args_schema: Type[BaseModel] = FinnhubMarketNewsInput
    description: str = "Use Finnhubs API to get the latest market news."
    agent_id: int = None

    def _execute(self, category='general', min_id=0):
        api_key = self.get_tool_config("FINNHUB_API_KEY")
        finnhub_client = Client(api_key=api_key)
        return finnhub_client.general_news(category=category, min_id=min_id)
