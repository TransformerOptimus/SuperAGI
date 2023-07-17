from finnhub import Client
from pydantic import BaseModel, Field
from typing import Type, Optional
from superagi.tools.base_tool import BaseTool

class FinnhubQuoteInput(BaseModel):
    symbol: str = Field(..., description="Company symbol to look up")

class FinnhubQuoteTool(BaseTool):
    name: str = "Finnhub Quote Tool"
    args_schema: Type[BaseModel] = FinnhubQuoteInput
    description: str = "Use Finnhubs API to get the latest quote for an item (not real time)"
    agent_id: int = None

    def _execute(self, symbol: str):
        api_key = self.get_tool_config("FINNHUB_API_KEY")
        finnhub_client = Client(api_key=api_key)
        return finnhub_client.quote(symbol)
