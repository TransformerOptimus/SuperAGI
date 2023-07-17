from finnhub import Client
from pydantic import BaseModel, Field
from typing import Type, Optional
from superagi.tools.base_tool import BaseTool

class FinnhubBasicFinancialsInput(BaseModel):
    symbol: str = Field(..., description="Company symbol to look up")

class FinnhubBasicFinancialsTool(BaseTool):
    name: str = "Finnhub Basic Financials Tool"
    args_schema: Type[BaseModel] = FinnhubBasicFinancialsInput
    description: str = "Use Finnhubs API to get basic financials, such as margin, P/E ratio, 52-week high/low etc."
    agent_id: int = None

    def _execute(self, symbol: str):
        api_key = self.get_tool_config("FINNHUB_API_KEY")
        finnhub_client = Client(api_key=api_key)
        return finnhub_client.company_basic_financials(symbol, 'all')
