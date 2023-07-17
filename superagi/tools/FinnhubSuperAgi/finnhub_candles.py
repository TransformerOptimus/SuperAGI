from finnhub import Client
from pydantic import BaseModel, Field
from typing import Type, Optional
from superagi.tools.base_tool import BaseTool

class FinnhubCandlesInput(BaseModel):
    symbol: str = Field(..., description="Company symbol to look up")
    from_time: int = Field(..., description="From time")
    to_time: int = Field(..., description="To time")
    resolution: str = Field(..., description="Resolution: 1, 5, 15, 30, 60, (D), W, M")

class FinnhubCandlesTool(BaseTool):
    name: str = "Finnhub Stock Candles Tool"
    args_schema: Type[BaseModel] = FinnhubCandlesInput
    description: str = "Use Finnhubs API to look for stock candles"
    agent_id: int = None

    def _execute(self, symbol: str, from_time: int, to_time: int, resolution = 'D'):
        api_key = self.get_tool_config("FINNHUB_API_KEY")
        finnhub_client = Client(api_key=api_key)
        return finnhub_client.stock_candles(symbol=symbol, resolution=resolution, _from=int(from_time), to=int(to_time))
