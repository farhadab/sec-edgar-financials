import pytest
import re
from filings.edgar import *
	
def setup_module(module):
    print ("setup_module      module:%s" % module.__name__)

def test_get_filing_info():
	filing_headers, filing_infos = get_filing_info()
	assert filing_infos is not None
	assert type(filing_infos) is list

	for filing_info in filing_infos:
		validate_filing_info(filing_info)


def validate_filing_info(filing_info):
	validate_company(filing_info)
	validate_form(filing_info)
	validate_cik(filing_info)
	validate_date(filing_info)
	validate_url(filing_info)


def validate_company(filing_info):
	assert len(filing_info.company) > 0


def validate_form(filing_info):
	assert len(filing_info.form) > 0


def validate_cik(filing_info):
	assert len(filing_info.cik) > 0

	pattern = re.compile('[0-9]+')
	assert pattern.search(filing_info.url) is not None


def validate_date(filing_info):
	assert len(filing_info.date_filed) > 0

	pattern = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
	assert pattern.search(filing_info.date_filed) is not None


def validate_url(filing_info):
	assert len(filing_info.url) > 0

	pattern = re.compile('(https:\\/\\/www.sec.gov\\/Archives\\/edgar\\/data\\/)([^\\s]+)(\\.txt)')
	assert pattern.search(filing_info.url) is not None



def test_get_filing_info_forms():
	forms = ['4', '10-Q']
	filing_headers, filing_infos = get_filing_info(forms=forms)
	assert filing_infos is not None
	assert type(filing_infos) is list

	for filing_info in filing_infos:
		assert filing_info.form in forms