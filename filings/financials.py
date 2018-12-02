'''
Handles financial logic
'''
import re
from bs4 import BeautifulSoup
from json import JSONEncoder

class FinancialReportEncoder(JSONEncoder):
		
	def default(self, o):
		return o.__dict__



class FinancialElement:
	'''
	Models financial elements
	'''
	def __init__(self, label, value):
		self.label = label
		self.value = value

	def __repr__(self):
		return str(self.__dict__)



class FinancialInfo:
	'''
	Models financial data provided in a financial report
	financial elements are stored in a map to retain flexibility
	'''
	def __init__(self, date, months, map):
		self.date = date
		self.months = months
		self.map = map

	def __repr__(self):
		return str(self.__dict__)



class FinancialReport:
	'''
	Models financial reports from an edgar filing
	financial elements are stored in a map to retain flexibility
	'''
	def __init__(self, company, reports=[]):
		self.company = company
		self.reports = reports

	def add_financial_info(self, financial_info: FinancialInfo):
		self.reports.append(financial_info)

	def __repr__(self):
		return str(self.__dict__)

# https://pypi.org/project/python-xbrl/

'''
XBRL rules for us-gaap namespace are found at the site below
https://xbrl.us/data-rule/dqc_0015-le/

spreadsheet is in docs folder

Notes:
 - only accept us-gaap based filings

For 10-K or 10-Q
1. get 10-K/10-Q filing from filings list
2. for each filing, in the filing text doc, find the FilingSummary.xml
3. In FilingSummary.MyReports, find the Reports with ShortNames matching
   what's set in STATEMENT_SHORT_NAMES (lower case)
4. get the HtmlFileName of the Report
5. find the DOCUMENT with the given FILENAME in HtmlFileName
The next part differs based on 10-K and 10-Q
6. in the TEXT.html.body, get the data in the first table (class="report") and 
   parse. 
   a. Exclude the first row (title and 12 Months Ended text)
   b. Should have four columns, with the last three representing the 
      current year, last year, and two years ago (order may vary).
   c. Years will be in th elements (class="th"), data in the td elements with
      class="nump"
   d. The first td in each row will tell us the us-gaap namespace elementName.
      This will be in the onclick of the a tag in the td, e.g.
        onclick="top.Show.showAR( this, 'defref_us-gaap_CostOfGoodsSold'...
      Some might not have us-gaap, e.g.
        defref_air_OperatingIncomeLossIncludingIncomeLossFromEquityMethodInvestments
      though this should be defref_us-gaap_OperatingIncomeLoss
   e. millions? Assume yes. th in first row with class="t1", div.strong:
        Consolidated Statements Of Operations - USD ($)<br> shares in Millions,
        $ in Millions
'''
NUM_META_DATA_ROWS = 2


def get_financial_report(company, financial_html_text):
	financial_info = process_financial_info(financial_html_text)
	financial_report = FinancialReport(company, financial_info)
	print(FinancialReportEncoder().encode(financial_report)) # for easy QA using JSON
	return financial_report


def process_financial_info(financial_html_text):
	'''
	Return [...] from the html text containing the financial data
	'''
	source_soup = BeautifulSoup(financial_html_text, 'html.parser')
	report = source_soup.find('table', {'class':'report'})
	rows = report.find_all('tr')

	financial_info = []

	dates, period_units, unit_text = _get_statement_meta_data(rows)

	for i, date in enumerate(dates):
		financial_info += [FinancialInfo(date, period_units[i], {})]

	for row_num, row in enumerate(rows[NUM_META_DATA_ROWS:]):
		data = row.find_all('td')

		xbrl_element = None
		label = None
		numeric_data_available = False

		for index, info in enumerate(data):
			info_text = info.get_text().replace('\n', '')
			class_list = info.attrs['class']

			processed_financial_value = None

			if 'pl' in class_list:
				# pl class indicates the td is the financial label
				xbrl_element = _process_xbrl_element(info)
				# print(xbrl_element)
				label = info_text

			elif 'nump' in class_list or 'num' in class_list:
				# nump class indicates td, and so more generally, the row, has numeric data
				numeric_data_available = True
				processed_financial_value = _process_financial_value(info_text, xbrl_element, unit_text)

			elif 'text' in class_list:
				if numeric_data_available:
					# this corner case occurs when a given element appears sparsely (e.g. not collected in every period)
					processed_financial_value = _process_financial_value(info_text, xbrl_element, unit_text)
				# else:
				# 	# super label (abstract - no financial data)
				# 	print(xbrl_element)

			if processed_financial_value is not None:
				financial_info[index-1].map[xbrl_element] = FinancialElement(label, processed_financial_value)


	return financial_info


def _get_statement_meta_data(rows):
	dates = []
	period_units = []
	unit_text = None

	# we only use the first two rows
	if(len(rows)<NUM_META_DATA_ROWS):
		print('not enough rows of data')
	else:
		for row_num, row in enumerate(rows[:NUM_META_DATA_ROWS]):
			# meta data comes from the table headers
			data = row.find_all('th')

			for index, info in enumerate(data):
				info_text = info.get_text().replace('\n', '')

				class_list = info.attrs['class']
				
				if row_num == 0:

					if 'tl' in class_list:
						# first th with tl class has title and unit specification
						info_list = info.find('div').get_text('|', strip=True).split('|')
						# e.g. shares in Thousands, $ in Millions
						unit_text = info_list[1]
						# e.g. CONSOLIDATED STATEMENTS OF INCOME - USD ($)
						title = info_text.replace(unit_text, '').strip()

					elif 'th' in class_list:
						# Period unit of measurement (e.g. 12 Months Ended)
						# Balance sheets are a snapshot, so no period
						try:
							for col in range(int(info.attrs['colspan'])):
								period_units = period_units + [_process_period(info_text)] # usually months; use regex for #?
						except KeyError:
							period_units = period_units + [None]
							dates = dates + [info_text]


				elif row_num == 1 and 'th' in class_list:
					# second row indicates dates of data to come
					dates = dates + [info_text]

	return dates, period_units, unit_text


def _process_period(info_text):
	return int(re.sub('[^0-9]', '', info_text))


def _process_xbrl_element(info):
	'''
	Returns the name of the XBRL element in info (html BeautifulSoup).
	Leaving "us-gaap_" prefix in so it's contains both the namespace
	and elementName of the XBRL (in case it's not always us-gaap) 
	'''
	# us-gaap namespace element is in the onclick of the anchor tag
	anchor = info.find('a')
	onclick_attr = anchor.attrs['onclick']
	# strip javascript
	xbrl_element = onclick_attr.replace(
		'top.Show.showAR( this, \'defref_', ''
		).replace('\', window );', '')

	return xbrl_element


def _process_financial_value(text, xbrl_element, unit_text):
	'''
	Returns float representation of text after stripping special characters
	'''
	is_negative = True if '(' in text else False
	# strip special characters
	amount_text = re.sub('[^0-9\\.]', '', text)
	value = None

	try:
		amount = float(amount_text)
		value = -amount if is_negative else amount

		# handle units
		if('PerShare' in xbrl_element):
			value = value # no change
		elif (('Shares' in xbrl_element and 'shares in billions' in unit_text.lower())
			or ('Shares' not in xbrl_element and '$ in billions' in unit_text.lower())):
			value = value * 1000000000
		elif (('Shares' in xbrl_element and 'shares in millions' in unit_text.lower())
			or ('Shares' not in xbrl_element and '$ in millions' in unit_text.lower())):
			value = value * 1000000
		elif (('Shares' in xbrl_element and 'shares in thousands' in unit_text.lower())
			or ('Shares' not in xbrl_element and '$ in thousands' in unit_text.lower())):
			value = value * 1000

	except ValueError:
		print(amount_text+' is not numeric')

	return value



