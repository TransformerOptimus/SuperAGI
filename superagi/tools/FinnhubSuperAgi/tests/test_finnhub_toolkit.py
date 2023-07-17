import pytest
from datetime import datetime
from FinnhubSuperAgi_toolkit import FinnhubToolkit
from finnhub_basic_financials import FinnhubBasicFinancialsTool
from finnhub_candles import FinnhubCandlesTool
from finnhub_company_news import FinnhubCompanyNewsTool
from finnhub_market_news import FinnhubMarketNewsTool
from finnhub_quote import FinnhubQuoteTool
from finnhub_technical_indicators import FinnhubTechnicalIndicatorsTool

class TestFinnhubToolkit():
    
    toolkit = FinnhubToolkit()
    symbol = 'AAPL'
    now = (datetime(2023, 7, 7) - datetime(1970, 1, 1)).total_seconds()
    three_days_ago = three_days_ago = now - 3 * 24 * 60 * 60
        
    def test_company_news(self):
        company_news = self.toolkit.get_tools()[0]
        assert isinstance(company_news, FinnhubCompanyNewsTool)
        result = company_news._execute(self.symbol, from_date="2023-07-07", to_date="2023-07-08")
        assert result
        
    def test_candles(self):
        candles = self.toolkit.get_tools()[1]
        assert isinstance(candles, FinnhubCandlesTool)
        
        result = candles._execute(symbol=self.symbol, from_time=self.three_days_ago, to_time=self.now)
        print(f'candles {result}')
        expected = {'c': [191.33, 191.81, 190.68], 'h': [192.98, 192.02, 192.67], 'l': [190.62, 189.2, 190.24], 'o': [191.565, 189.84, 191.41], 's': 'ok', 't': [1688515200, 1688601600, 1688688000], 'v': [46920261, 45156009, 46814998]}
        assert result == expected
        
    def test_basic_financials(self):
        basic_financials = self.toolkit.get_tools()[2]
        assert isinstance(basic_financials, FinnhubBasicFinancialsTool)
        result = basic_financials._execute(symbol=self.symbol)
        assert result
    
    def test_technical_indicators(self):
        technical_indicators = self.toolkit.get_tools()[3]
        assert isinstance(technical_indicators, FinnhubTechnicalIndicatorsTool)
        
        result = technical_indicators._execute(symbol=self.symbol, indicator= 'sma' , from_time=self.three_days_ago, to_time=self.now, timeperiod=1)
        print(f'ti {result}')
        expected = {'c': [191.33, 191.81, 190.68], 'h': [192.98, 192.02, 192.67], 'l': [190.62, 189.2, 190.24], 'o': [191.565, 189.84, 191.41], 's': 'ok', 'sma': [191.33, 191.81, 190.68], 't': [1688515200, 1688601600, 1688688000], 'v': [46920261, 45156009, 46814998]}
        assert result == expected
    
    def test_quote(self):
        quote = self.toolkit.get_tools()[4]
        assert isinstance(quote, FinnhubQuoteTool)
    
        result = quote._execute(symbol=self.symbol)
    
        assert result
        assert len(result) == 8
        
    def test_market_news(self):
        market_news = self.toolkit.get_tools()[5]
        assert isinstance(market_news, FinnhubMarketNewsTool)
    
        result = market_news._execute()
        assert result
 
