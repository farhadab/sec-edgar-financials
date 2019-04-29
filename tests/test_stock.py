import pytest
import json
from edgar.stock import Stock, NoFilingInfoException
from edgar.financials import FinancialReportEncoder

    
def setup_module(module):
    print('setup_module      module:%s' % module.__name__)


def test_init():

    stock = Stock(symbol='AAPL')
    assert stock.symbol == 'AAPL'
    assert stock.cik == '320193'

def test_get_filing():

    stock = Stock(symbol='AAPL')
    filing = stock.get_filing(period='quarterly', year=2016, quarter=1)
    assert True



############## Negative Testing ##############

def test_init_unknown_symbol():
    try:
        Stock(symbol='ZZZZZZZZZZZZZZZ')
        assert False
    except IndexError:
        assert True

def test_get_filing_no_filing_found_exception():

    stock = Stock(symbol='FB')
    try:
        # IPO was in 2012
        filing = stock.get_filing(period='quarterly', year=2011, quarter=1)
        assert False
    except NoFilingInfoException:
        assert True