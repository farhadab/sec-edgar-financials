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
    # ensure certain data points are correct
    revenue = result.reports[0].map['us-gaap_SalesRevenueNet'].value
    assert revenue == 75872000000.0

def test_get_statement_of_earnings():
    # synonymous with income statement
    stock = Stock(symbol='IBM')
    filing = stock.get_filing(period='annual', year=2018, quarter=1)
    result = filing.get_income_statements()
    print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
    # ensure certain data points are correct
    revenue = result.reports[0].map['us-gaap_Revenues'].value
    assert revenue == 79139000000.0

def test_get_balance_sheets():

    stock = Stock(symbol='SPWR')
    filing = stock.get_filing(period='quarterly', year=2018, quarter=4)
    result = filing.get_balance_sheets()
    print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
    # ensure certain data points are correct
    assets = result.reports[0].map['us-gaap_Assets'].value
    assert assets == 3126117000.0

def test_get_statement_of_financial_position():
    # synonymous with balance sheet
    stock = Stock(symbol='IBM')
    filing = stock.get_filing(period='annual', year=2018, quarter=1)
    result = filing.get_balance_sheets()
    print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
    # ensure certain data points are correct
    assets = result.reports[0].map['us-gaap_Assets'].value
    assert assets == 125356000000.0

def test_get_cash_flows():

    stock = Stock(symbol='SPWR')
    filing = stock.get_filing(period='quarterly', year=2018, quarter=4)
    result = filing.get_cash_flows()
    print(FinancialReportEncoder().encode(result)) # for easy QA using JSON
    # ensure certain data points are correct
    profit_loss = result.reports[0].map['us-gaap_ProfitLoss'].value
    assert profit_loss == -745351000.0