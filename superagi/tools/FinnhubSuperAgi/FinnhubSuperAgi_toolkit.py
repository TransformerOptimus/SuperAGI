from abc import ABC
from typing import List

from superagi.tools.base_tool import BaseTool, BaseToolkit
from finnhub_basic_financials import FinnhubBasicFinancialsTool
from finnhub_candles import FinnhubCandlesTool
from finnhub_company_news import FinnhubCompanyNewsTool
from finnhub_market_news import FinnhubMarketNewsTool
from finnhub_quote import FinnhubQuoteTool
from finnhub_technical_indicators import FinnhubTechnicalIndicatorsTool

class FinnhubToolkit(BaseToolkit, ABC):
    name: str = "FinnhubToolkit"
    description: str = "Toolkit that contains various tools to interact with Finnhubs api to get financial information"

    def get_tools(self) -> List[BaseTool]:
        return [FinnhubCompanyNewsTool(), FinnhubCandlesTool(), FinnhubBasicFinancialsTool(), FinnhubTechnicalIndicatorsTool(), FinnhubQuoteTool(), FinnhubMarketNewsTool()]

    def get_env_keys(self) -> List[str]:
        return ["FINNHUB_API_KEY"]
