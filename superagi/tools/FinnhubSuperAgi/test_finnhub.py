from datetime import datetime
import finnhub
from FinnhubSuperAgi_toolkit import FinnhubToolkit
from finnhub_basic_financials import FinnhubBasicFinancialsTool
from finnhub_candles import FinnhubCandlesTool
from finnhub_company_news import FinnhubCompanyNewsTool
from finnhub_market_news import FinnhubMarketNewsTool
from finnhub_quote import FinnhubQuoteTool
from finnhub_technical_indicators import FinnhubTechnicalIndicatorsTool

def test_finnhub_toolkit():
    
    toolkit = FinnhubToolkit()
    symbol = 'AAPL'

    
    # news    
    company_news = toolkit.get_tools()[0]
    assert isinstance(company_news, FinnhubCompanyNewsTool)
    result = company_news._execute(symbol, from_date="2023-07-07", to_date="2023-07-08")
    assert result

    # candles
    now = (datetime(2023, 7, 7) - datetime(1970, 1, 1)).total_seconds()
    three_days_ago = now - 3 * 24 * 60 * 60
    candles = toolkit.get_tools()[1]
    assert isinstance(candles, FinnhubCandlesTool)
    
    result = candles._execute(symbol=symbol, from_time=three_days_ago, to_time=now)

    expected = {'c': [191.33, 191.81], 'h': [192.98, 192.02], 'l': [190.62, 189.2], 'o': [191.565, 189.84], 's': 'ok', 't': [1688515200, 1688601600], 'v': [46920261, 45156009]}

    assert result == expected


    # basic financials
    basic_financials = toolkit.get_tools()[2]
    assert isinstance(basic_financials, FinnhubBasicFinancialsTool)

    result = basic_financials._execute(symbol=symbol)
    assert result

    # technical indicators
    technical_indicators = toolkit.get_tools()[3]
    assert isinstance(technical_indicators, FinnhubTechnicalIndicatorsTool)
    
    result = technical_indicators._execute(symbol=symbol, from_time=three_days_ago, to_time=now, timeperiod=1)

    expected = {'c': [191.33, 191.81], 'h': [192.98, 192.02], 'l': [190.62, 189.2], 'o': [191.565, 189.84], 's': 'ok', 'sma': [191.33, 191.81], 't': [1688515200, 1688601600], 'v': [46920261, 45156009]}

    assert result == expected

    # quote
    quote = toolkit.get_tools()[4]
    assert isinstance(quote, FinnhubQuoteTool)

    result = quote._execute(symbol=symbol)

    assert result
    assert len(result) == 8

    # market news
    market_news = toolkit.get_tools()[5]
    assert isinstance(market_news, FinnhubMarketNewsTool)

    result = market_news._execute()

    assert result


if __name__ == "__main__":
    test_finnhub_toolkit()
