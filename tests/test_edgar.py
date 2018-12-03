import pytest
import re
from datetime import datetime
from filings.edgar import get_filing_info, SUPPORTED_FORMS, InvalidInputException
	
def setup_module(module):
	print('setup_module      module:%s' % module.__name__)

############## Positive Testing ##############

def test_get_filing_info():
	filing_headers, filing_infos = get_filing_info(year=2018, quarter=4)
	# print(filing_infos)
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



def test_get_filing_info_forms_filter():
	forms = ['4', '10-Q']
	filing_headers, filing_infos = get_filing_info(forms=forms, year=2018, quarter=4)
	assert filing_infos is not None
	assert type(filing_infos) is list

	for filing_info in filing_infos:
		assert filing_info.form in forms



def test_get_filing_info_cik_filter():
	cik = '1698878'
	filing_headers, filing_infos = get_filing_info(cik=cik, year=2018, quarter=4)
	assert filing_infos is not None
	assert type(filing_infos) is list

	for filing_info in filing_infos:
		assert filing_info.cik == cik


############## Negative Testing ##############

def test_get_filing_info_bad_form():
	forms = ['4', '10-Z']
	try:
		get_filing_info(forms=forms, year=2018, quarter=4)
		assert False
	except InvalidInputException:
	    assert True

def test_get_filing_info_bad_year():
	try:
		get_filing_info(year=20181, quarter=4)
		assert False
	except InvalidInputException:
	    assert True
	try:
		get_filing_info(year=1992, quarter=4)
		assert False
	except InvalidInputException:
	    assert True
	current_year = datetime.now().year
	try:
		get_filing_info(year=current_year+1, quarter=4)
		assert False
	except InvalidInputException:
	    assert True

def test_get_filing_info_bad_quarter():
	try:
		get_filing_info(year=2018, quarter=5)
		assert False
	except InvalidInputException:
	    assert True
	try:
		get_filing_info(year=2018, quarter=-1)
		assert False
	except InvalidInputException:
	    assert True
	try:
		get_filing_info(year=2018, quarter=0.25)
		assert False
	except InvalidInputException:
	    assert True


