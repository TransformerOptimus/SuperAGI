from finnhub import Client
from pydantic import BaseModel, Field
from typing import Type, Optional
from superagi.tools.base_tool import BaseTool

class FinnhubCompanyNewsInput(BaseModel):
    symbol: str = Field(..., description="Company symbol to look up")
    from_date: str = Field(..., description="From date, inclusive")
    to_date: str = Field(..., description="To date, inclusive")

class FinnhubCompanyNewsTool(BaseTool):
    name: str = "Finnhub Company News Tool"
    args_schema: Type[BaseModel] = FinnhubCompanyNewsInput
    description: str = "Use Finnhubs API to look for company news"
    agent_id: int = None

    def _execute(self, symbol: str, from_date: str, to_date: str):
        api_key = self.get_tool_config("FINNHUB_API_KEY")
        finnhub_client = Client(api_key=api_key)
        return finnhub_client.company_news(symbol, _from=from_date, to=to_date)
