'''
This file will be used to traverse the EDGAR filing system and determine
the location of filings

https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm

The EDGAR indexes list the following information for each filing: Company Name,
Form Type, CIK (Central Index Key), Date Filed, and File Name (including folder
path).

Four types of indexes are available. The company, form, and master indexes
contain the same information sorted differently.

company — sorted by company name
form — sorted by form type
master — sorted by CIK number
XBRL — list of submissions containing XBRL financial files, sorted by CIK
	number; these include Voluntary Filer Program submissions

Forms that we'll be concerned with (all forms are listed at
https://www.sec.gov/forms):
	10-Q: quarterly report and financial statements
	10-K: annual report and financial statements
	8-K: important events (commonly filed)
	4: insider trading (gets us the stock symbol (issuerTradingSymbol))
These can all have ammendments made, e.g. 10-Q/A
'''
from edgar.requests_wrapper import GetRequest
import json
import re
from datetime import datetime
import os


SYMBOLS_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'symbols.csv')


FINANCIAL_FORM_MAP = {
	'annual': ['10-K','10-K/A'],
	'quarterly': ['10-Q','10-Q/A'],
}
SUPPORTED_FORMS = FINANCIAL_FORM_MAP['annual'] + FINANCIAL_FORM_MAP['quarterly'] + ['3', '4', '5']

EDGAR_MIN_YEAR = 1993

ARCHIVES_URL = 'https://www.sec.gov/Archives/'
FULL_INDEX_URL = ARCHIVES_URL+'edgar/full-index/'
INDEX_JSON = 'index.json'
# company.idx gives us a list of all companies that filed in the period
COMPANY_IDX = 'company.idx' # sorted by company name
FORM_IDX = 'form.idx' # sorted by form type
#MASTER_IDX = 'master.idx' # sorted by cik
#CRAWLER_IDX = 'crawler.idx'
#XBRL_IDX = 'xbrl.idx'


# don't need the following structures, commenting them just in case
# class Directory():
# 	'''
# 	Directory and Item classes will be used to help model and serve as a reference
# 	'''
# 	def __init__(self, item, name, parent_dir):
# 		self.item = item # array of items in the directory
# 		self.name = name # name of the directory
# 		self.parent_dir = parent_dir # location of parent directory

# class Item():
# 	def __init__(self, last_modified, name, type, href, size):
# 		self.last_modified = last_modified # MM/dd/YYYY hh:mm:ss AM/PM
# 		self.name = self.name
# 		self.type = self.type # dir or file
# 		self.href = self.href # relative to directory
# 		self.size = self.size



class FilingInfo:
	'''
	FilingInfo class will model crawler.idx filing information
	'''
	def __init__(self, company, form, cik, date_filed, file):
		self.company = company
		self.form = form
		self.cik = cik
		self.date_filed = date_filed
		self.url = ARCHIVES_URL+file

	def __repr__(self):
		return '[{0}, {1}, {2}, {3}, {4}]'.format(
			self.company, self.form, self.cik, self.date_filed, self.url)
		


def get_index_json(year='', quarter=''):
	'''
	Returns json of index.json
		year and quarter are defaulted to '', but can be replaced with an item.href
		from index.json
	'''
	url = FULL_INDEX_URL+year+quarter+INDEX_JSON
	# print('getting data at '+url)

	response = GetRequest(url).response
	text = response.text

	json_text = json.loads(text)
	#print(text)
	#print(json['directory']['item'][0]['href'])
	return json_text



def get_filing_info(cik='', forms=[], year=0, quarter=0):
	current_year = datetime.now().year

	if year!=0 and ((len(str(year)) != 4) or year < EDGAR_MIN_YEAR or year > current_year):
		raise InvalidInputException('{} is not a supported year'.format(year))
	if quarter not in [0, 1, 2, 3, 4]:
		raise InvalidInputException('Quarter must be 1, 2, 3, or 4. 0 indicates default (latest)')

	return _get_filing_info(cik=cik, forms=forms, year=('' if year==0 else str(year)+'/'), quarter=('' if quarter==0 else 'QTR{}/'.format(quarter)))


def _get_filing_info(cik='', forms=[], year='', quarter=''):
	'''
	Return a tuple of (filing_info_headers, filing_info); filing_info is a List of FilingInfo
		If forms are specified, only filings with the given value will be returned
		e.g. 10-K, 10-Q, 3, 4, 5
		year and quarter are defaulted to '', but can be replaced with an item.href
		from index.json
	'''
	# can use form.idx to order by form type, but headers are in different order
	# so would need to change code for this
	for form in forms:
		if form not in SUPPORTED_FORMS:
			raise InvalidInputException('{} is not a supported form'.format(form))

	url = '{}{}{}{}'.format(FULL_INDEX_URL, year, quarter, COMPANY_IDX)
	print('getting filing info from '+url)

	response = GetRequest(url).response
	text = response.text
	# print(text)

	# we just want the filing info data, which starts after the "Company Name"
	# header and ends at the File Name (for company.idx)
	header_start_index = text.find('\nCompany Name')
	header_end_index = text.find('File Name', header_start_index)+len('File Name')
	header_text = text[header_start_index:header_end_index].replace('\n', '')

	filing_info_text = text[text.index(header_text):]
	# this also gives us the starting index for the data, e.g.:
	'''
	Company Name                                                  Form Type   CIK         Date Filed  File Name
	---------------------------------------------------------------------------------------------------------------------------------------------
	01VC Fund II, L.P.                                            D           1746009     2018-07-20  edgar/data/1746009/0001213900-18-009448.txt         
	1 800 FLOWERS COM INC                                         3           1084869     2018-07-13  edgar/data/1084869/0001084869-18-000016.txt         
	1 800 FLOWERS COM INC                                         4           1084869     2018-07-03  edgar/data/1084869/0001084869-18-000015.txt  
	'''

	# split filing_info_text into rows
	filing_info_text_list = filing_info_text.split('\n')

	# split filing_list into usable data
	company_index = header_text.index('Company Name')
	form_index = header_text.index('Form Type')
	cik_index = header_text.index('CIK')
	date_index = header_text.index('Date Filed')
	file_index = header_text.index('File Name')

	filing_info_raw = [
						FilingInfo(
						row[company_index:form_index].strip(), # Company Name
						row[form_index:cik_index].strip(), # Form Type
						row[cik_index:date_index].strip(), # CIK
						row[date_index:file_index].strip(), # Date Filed
						row[file_index:len(row)].strip() # File Name
						)
						 for index, row in enumerate(filing_info_text_list) 
						 	if row.strip() != '' and
						 	(index == 0 or (
						 		index != 1 and # ignore separator row
								# Form Type should among forms or forms be default (all)
								(row[form_index:cik_index].strip() in forms or forms == [])
								# CIK should match cik or be default
								and (row[cik_index:date_index].strip() == cik or cik == '')
							))
					]

	# initialize empty in case no matches for forms
	filing_info_headers = []
	filing_info = []

	if len(filing_info_raw) > 0:
		# header is the first row (same as header_text)
		filing_info_headers = filing_info_raw[0]
		# data is from the 2nd row (after hearder) onwards
		filing_info = list(filter(None, filing_info_raw))[1:]

	return filing_info_headers, filing_info



def get_financial_filing_info(period, cik, year='', quarter=''):
	if period not in FINANCIAL_FORM_MAP:
		raise KeyError('period must be either "annual" or "quarterly"')

	forms = FINANCIAL_FORM_MAP[period]
	return get_filing_info(cik=cik, forms=forms, year=year, quarter=quarter)[1]



########## Exceptions ##########
class InvalidInputException(Exception):
	pass