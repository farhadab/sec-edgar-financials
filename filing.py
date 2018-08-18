import requests
import json
import re


'''
This file will be used to gather EDGAR filing data

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
	8-k: important events (commonly filed)
	4: insider trading (gets us the stock symbol (issuerTradingSymbol))
'''
ARCHIVES_URL = 'https://www.sec.gov/Archives/'
FULL_INDEX_URL = ARCHIVES_URL+'edgar/full-index/'
INDEX_JSON = 'index.json'
# company.idx gives us a list of all companies that filed in the period
COMPANY_IDX = 'company.idx'
#CRAWLER_IDX = 'crawler.idx'
#XBRL_IDX = 'xbrl.idx'



class Directory():
	'''
	Directory and Item classes will be used to help model and serve as a reference
	'''
	def __init__(self, item, name, parent_dir):
		self.item = item # array of items in the directory
		self.name = name # name of the directory
		self.parent_dir = parent_dir # location of parent directory

class Item():
	def __init__(self, last_modified, name, type, href, size):
		self.last_modified = last_modified # MM/dd/YYYY hh:mm:ss AM/PM
		self.name = self.name
		self.type = self.type # dir or file
		self.href = self.href # relative to directory
		self.size = self.size


def get_index_json(year='', quarter=''):
	'''
	Returns json of index.json
		year and quarter are defaulted to '', but can be replaced with an item.href
		from index.json
	'''
	url = FULL_INDEX_URL+year+quarter+INDEX_JSON

	index = requests.get(url)
	text = index.text
	json_text = json.loads(text)
	#print(text)
	#print(json['directory']['item'][0]['href'])
	return json_text


class Filing():
	'''
	Filing class will model crawler.idx filing data
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


def get_filings(year='', quarter=''):
	'''
	Return a tuple of (filing_headers, filings); filings has filing data
		year and quarter are defaulted to '', but can be replaced with an item.href
		from index.json
	'''
	url = FULL_INDEX_URL+year+quarter+COMPANY_IDX

	index = requests.get(url)
	text = index.text

	# we just want the filing list data, which starts after the "Company Name"
	# header and ends at the File Name (for company.idx)
	header_start_index = text.find('\nCompany Name')
	header_end_index = text.find('File Name', header_start_index)+len('File Name')
	header_text = text[header_start_index:header_end_index].replace('\n', '')

	filing_list_text = text[text.index(header_text):]
	#print(filing_list_text)
	# this also gives us the starting index for the data, e.g.:
	'''
	Company Name                                                  Form Type   CIK         Date Filed  File Name
	---------------------------------------------------------------------------------------------------------------------------------------------
	01VC Fund II, L.P.                                            D           1746009     2018-07-20  edgar/data/1746009/0001213900-18-009448.txt         
	1 800 FLOWERS COM INC                                         3           1084869     2018-07-13  edgar/data/1084869/0001084869-18-000016.txt         
	1 800 FLOWERS COM INC                                         4           1084869     2018-07-03  edgar/data/1084869/0001084869-18-000015.txt  
	'''

	# split text into rows
	filing_list = filing_list_text.split('\n')

	# split filing_list into usable data
	company_index = header_text.index('Company Name')
	form_index = header_text.index('Form Type')
	cik_index = header_text.index('CIK')
	date_index = header_text.index('Date Filed')
	file_index = header_text.index('File Name')

	filing_list_data = [
						Filing(
						row[company_index:form_index].strip(), # Company Name
						row[form_index:cik_index].strip(), # Form Type
						row[cik_index:date_index].strip(), # CIK
						row[date_index:file_index].strip(), # Date Filed
						row[file_index:len(row)].strip() # File Name
						)
						 for row in filing_list if row.strip() != ''
						]

	# header is the first row (same as header_text)
	filing_headers = filing_list_data[0]
	# data is from the third row (after hearder and separator rows) onwards
	filings = list(filter(None, filing_list_data))[2:]

	return filing_headers, filings


def test_get_filings(year='', quarter=''):
	'''
	TODO: Move to another module and import pytest
	Validates get_filings()
		year and quarter are defaulted to '', but can be replaced with an item.href
		from index.json
	'''
	filing_headers, filings = get_filings(year, quarter)
	# QA results
	#print(filing_headers)
	#print(filings[:100])
	for filing in filings:
		# validate date of filing
		date_regex = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
		if date_regex.search(filing.date_filed) is None: 
			print('Date filed is wrong: '+filing.date_filed)
			print(filing)


def get_all_forms(filings, form):
	'''
	Return a list of filings that have the given form
	'''
	return [filing for filing in filings if filing.form == form]