from finnhub import Client
from pydantic import BaseModel, Field
from typing import Type, Optional
from superagi.tools.base_tool import BaseTool

class FinnhubTechnicalIndicatorsInput(BaseModel):
    symbol: str = Field(..., description="Company symbol to look up")
    from_time: int = Field(..., description="From time")
    to_time: int = Field(..., description="To time")
    resolution: str = Field(..., description="Resolution: 1, 5, 15, 30, 60, (D), W, M")
    indicator: str = Field(..., description="Indicator. Ex: (sma), ema, wma, macd, bbands")
    timeperiod: str = Field(..., description="Time period. Default: 3")

class FinnhubTechnicalIndicatorsTool(BaseTool):
    name: str = "Finnhub Stock Technical Indicators Tool"
    args_schema: Type[BaseModel] = FinnhubTechnicalIndicatorsInput
    description: str = "Use Finnhubs API to look up technical indicators. Ex: sma, ema, wma, macd, bbands"
    agent_id: int = None

    def _execute(self, symbol: str, from_time: int, to_time: int, resolution = 'D', indicator = 'sma', timeperiod = 3):
        api_key = self.get_tool_config("FINNHUB_API_KEY")
        finnhub_client = Client(api_key=api_key)
        return finnhub_client.technical_indicator(symbol=symbol, resolution=resolution, _from=int(from_time), to=int(to_time), indicator=indicator, indicator_fields={"timeperiod": int(timeperiod)})
