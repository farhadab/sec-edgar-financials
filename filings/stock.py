'''
This module ties it all together; it will be the main module that's used 
'''
import pandas as pd
from filings.edgar import get_financial_filing_info
from filings.filing import Filing

class Stock:
	def __init__(self, symbol, period='annual', year='', quarter=''):
		self.symbol = symbol
		self.cik = self._find_cik()
		self.period = period
		self.filing = self._get_filing(period, year, quarter)


	def _find_cik(self):
		df = pd.read_csv('./symbols/symbols.csv', converters={'cik' : str})
		try:
			cik = df.loc[df['symbol'] == self.symbol]['cik'].iloc[0]
			print('cik for {} is {}'.format(self.symbol, cik))
			return cik
		except IndexError as e:
			raise IndexError('could not find cik, must add to symbols.csv') from None


	def _get_filing(self, period, year='', quarter=''):
		filing_info_list = get_financial_filing_info(period=period, cik=self.cik, year=year, quarter=quarter)

		if len(filing_info_list) == 0:
			raise NoFilingInfoException('No filing info found. Try a different period, year, and/or quarter.')

		filing_info = filing_info_list[0]

		url = filing_info.url
		filing = Filing(company=self.symbol, url=url)

		return filing


	def get_statements_of_income(self):
		return self.filing.get_statements_of_income()

	def get_balance_sheets(self):
		return self.filing.get_balance_sheets()

	def get_cash_flows(self):
		return self.filing.cash_flows()



class NoFilingInfoException(Exception):
	pass

period = 'quarterly'
stock = Stock(symbol='SPWR', period=period)
stock.get_statements_of_income()
stock.get_balance_sheets()
stock.get_cash_flows()
