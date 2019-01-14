import pytest
import json
from edgar.stock import Stock
from edgar.financials import FinancialReportEncoder

	
def setup_module(module):
	print('setup_module      module:%s' % module.__name__)


###############################################################################
############################# these are all TODOs #############################
###############################################################################
# just noting interesting cases here so i know to account for them

def test_get_income_statements():

	period = 'quarterly' # or 'annual', which is the default for Stock()
	# e.g. the next line will give you just the latest annual results
	# stock = Stock('AAPL')
	year = 2016
	quarter = 1 # 1, 2, 3, or 4
	stock = Stock(symbol='AAPL', period=period, year=year, quarter=quarter)
	result = stock.get_income_statements()
	print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
	# mock up info
	assert 1 == 1

def test_get_statement_of_earnings():
	# synonymous with income statement
	period = 'annual' # or 'annual', which is the default for Stock()
	# e.g. the next line will give you just the latest annual results
	# stock = Stock('AAPL')
	year = 2018
	quarter = 1 # 1, 2, 3, or 4
	stock = Stock(symbol='IBM', period=period, year=year, quarter=quarter)
	result = stock.get_income_statements()
	print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
	# mock up info
	assert 1 == 1

def test_get_balance_sheets():

	period = 'quarterly' # or 'annual', which is the default for Stock()
	# e.g. the next line will give you just the latest annual results
	# stock = Stock('AAPL')
	year = 2018
	quarter = 4 # 1, 2, 3, or 4
	stock = Stock(symbol='SPWR', period=period, year=year, quarter=quarter)
	result = stock.get_balance_sheets()
	print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
	# mock up info
	assert 1 == 1

def test_get_statement_of_financial_position():
	# synonymous with balance sheet
	period = 'annual' # or 'annual', which is the default for Stock()
	# e.g. the next line will give you just the latest annual results
	# stock = Stock('AAPL')
	year = 2018
	quarter = 1 # 1, 2, 3, or 4
	stock = Stock(symbol='IBM', period=period, year=year, quarter=quarter)
	result = stock.get_balance_sheets()
	print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
	# mock up info
	assert 1 == 1

def test_get_cash_flows():

	period = 'quarterly' # or 'annual', which is the default for Stock()
	# e.g. the next line will give you just the latest annual results
	# stock = Stock('AAPL')
	year = 2018
	quarter = 4 # 1, 2, 3, or 4
	stock = Stock(symbol='SPWR', period=period, year=year, quarter=quarter)
	result = stock.get_cash_flows()
	print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
	# mock up info
	assert 1 == 1



############## Negative Testing ##############

def test_init_unknown_symbol():
	try:
		Stock(symbol='ZZZZZZZZZZZZZZZ')
		assert False
	except IndexError:
	    assert True