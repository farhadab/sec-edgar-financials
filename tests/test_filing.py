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

    stock = Stock(symbol='AAPL')
    filing = stock.get_filing(period='quarterly', year=2016, quarter=1)
    result = filing.get_income_statements()
    print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
    # mock up info
    assert 1 == 1

def test_get_statement_of_earnings():
    # synonymous with income statement
    stock = Stock(symbol='IBM')
    filing = stock.get_filing(period='annual', year=2018, quarter=1)
    result = filing.get_income_statements()
    print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
    # mock up info
    assert 1 == 1

def test_get_balance_sheets():

    stock = Stock(symbol='SPWR')
    filing = stock.get_filing(period='quarterly', year=2018, quarter=4)
    result = filing.get_balance_sheets()
    print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
    # mock up info
    assert 1 == 1

def test_get_statement_of_financial_position():
    # synonymous with balance sheet
    stock = Stock(symbol='IBM')
    filing = stock.get_filing(period='annual', year=2018, quarter=1)
    result = filing.get_balance_sheets()
    print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
    # mock up info
    assert 1 == 1

def test_get_cash_flows():

    stock = Stock(symbol='SPWR')
    filing = stock.get_filing(period='quarterly', year=2018, quarter=4)
    result = filing.get_cash_flows()
    print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
    # mock up info
    assert 1 == 1