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
MASTER_IDX = 'master.idx' # sorted by cik
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



def get_latest_quarter_dir(year):
    '''
    Given a year (e.g. 2018), traverse the items in index.json to find
    the latest quarter, returning the number (e.g. 1, 2, 3, 4) and the
    reference in the system (e.g. 'QTR4/')
    '''
    year_str = str(year)+'/'
    index_json = get_index_json(year=year_str)
    items = index_json['directory']['item']

    # item list is in order, with the latest at the end
    for i in reversed(range(len(items))):
        item = items[i]

        if item['type'] == 'dir':
            # return the 
            return int(item['name'].replace('QTR','')), item['href']



def find_latest_filing_info_going_back_from(period, cik, year, quarter):
    '''
    Returns the latest filing info list in the given year, going backwards from
    the given year and quarter
    '''
    filing_info_list = []
    while quarter > 0 and len(filing_info_list) == 0:
        filing_info_list = get_financial_filing_info(period=period, cik=cik, year=year, quarter=quarter)
        quarter -= 1

    return filing_info_list


def get_filing_info(cik='', forms=[], year=0, quarter=0):
    '''
    Public wrapper to get FilingInfo for a given company, type of form, and 
    period
    '''
    current_year = datetime.now().year

    if year!=0 and ((len(str(year)) != 4) or year < EDGAR_MIN_YEAR or year > current_year):
        raise InvalidInputException('{} is not a supported year'.format(year))
    if quarter not in [0, 1, 2, 3, 4]:
        raise InvalidInputException('Quarter must be 1, 2, 3, or 4. 0 indicates default (latest)')

    year_str = '' if year==0 else str(year)+'/'
    quarter_str = '' if quarter==0 else 'QTR{}/'.format(quarter)

    if quarter == 0 and year != 0:
        # we just want the latest available
        quarter_str = get_latest_quarter_dir(year)[1]

    return _get_filing_info(cik=cik, forms=forms, year=year_str, quarter=quarter_str)


def _get_filing_info(cik='', forms=[], year='', quarter=''):
    '''
    Return a List of FilingInfo
        If forms are specified, only filings with the given value will be returned
        e.g. 10-K, 10-Q, 3, 4, 5
        year and quarter are defaulted to '', but can be replaced with an item.href
        from index.json
    '''
    def _get_raw_data(row):
        '''
        Returns a list from a string (master idx row) that is delimited by "|"

        Format of master.idx file is as follows:

        CIK|Company Name|Form Type|Date Filed|Filename
        --------------------------------------------------------------------------------
        1000209|MEDALLION FINANCIAL CORP|8-K|2019-01-08|edgar/data/1000209/0001193125-19-004285.txt
        1000209|MEDALLION FINANCIAL CORP|8-K|2019-01-11|edgar/data/1000209/0001193125-19-007413.txt
        1000228|HENRY SCHEIN INC|425|2019-01-07|edgar/data/1000228/0001193125-19-003023.txt
        '''
        return row.split('|')

    def _add_filing_info(filing_infos, data, forms):
        '''
        Adds a FilingInfo from data to a list

        :param data: list of length 5 with the following data indices:
            0=cik, 1=company, 2=form, 3=date_filed, 4=file_name 
        '''
        if len(data) == 5 and (forms == [] or data[2] in forms):
            # Form Type should among forms or forms be default (all)
            filing_infos.append(FilingInfo(
                        data[1], # Company Name
                        data[2], # Form Type
                        data[0], # CIK
                        data[3], # Date Filed
                        data[4].strip() # File Name
                    ))

    for form in forms:
        if form not in SUPPORTED_FORMS:
            raise InvalidInputException('{} is not a supported form'.format(form))

    # using master.idx so it's sorted by cik and we can use binary search
    url = '{}{}{}{}'.format(FULL_INDEX_URL, year, quarter, MASTER_IDX)
    print('getting {} filing info from {}'.format(forms, url))

    response = GetRequest(url).response
    text = response.text
    # print(text)
    rows = text.split('\n')
    data_rows = rows[11:]

    filing_infos = []

    if cik != '':
        # binary search to get company's filing info
        start = 0
        end = len(data_rows)

        while start < end:
            mid = (start+end)//2
            data = _get_raw_data(data_rows[mid])

            # comparisons are done as strings, same as ordering in master.idx
            # e.g. 11 > 100
            if data[0] == cik:
                # matched cik
                _add_filing_info(filing_infos, data, forms)

                # get all before and after (there can be multiple)
                # go backwards to get those before
                index = mid - 1
                data = _get_raw_data(data_rows[index])
                while data[0] == cik and index >= 0:
                    _add_filing_info(filing_infos, data, forms)
                    index -= 1
                    data = _get_raw_data(data_rows[index])

                # after
                index = mid + 1
                data = _get_raw_data(data_rows[index])
                while data[0] == cik and index < len(data_rows):
                    _add_filing_info(filing_infos, data, forms)
                    index += 1
                    data = _get_raw_data(data_rows[index])

                break

            elif data[0] < cik:
                start = mid + 1
            else:
                end = mid - 1
    else:
        # go through all
        for row in data_rows:
            data = _get_raw_data(row)
            _add_filing_info(filing_infos, data, forms)


    return filing_infos



def get_financial_filing_info(period, cik, year='', quarter=''):
    if period not in FINANCIAL_FORM_MAP:
        raise KeyError('period must be either "annual" or "quarterly"')

    forms = FINANCIAL_FORM_MAP[period]
    return get_filing_info(cik=cik, forms=forms, year=year, quarter=quarter)



########## Exceptions ##########
class InvalidInputException(Exception):
    pass