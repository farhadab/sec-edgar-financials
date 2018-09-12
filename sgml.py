import re
from bs4 import BeautifulSoup

'''
'''

# used in parsing financial data; these are the statements we'll be parsing
STATEMENT_SHORT_NAMES = [
	'consolidated statements of income'
	,'consolidated statements of operations'
	,'consolidated balance sheets'
	,'consolidated statements of cash flows'
	,'condensed consolidated statements of income (unaudited)'
	,'condensed consolidated balance sheets (current period unaudited)'
	,'condensed consolidated balance sheets (unaudited)'
	,'condensed consolidated statements of cash flows (unaudited)'
]


class FinancialInfo():
	'''
	Models financial data to be stored
	'''
	def __init__(self, element, label, period, date, value, unit):
		self.element = element
		self.label = label
		self.period = period
		self.date = date
		self.value = value
		self.unit = unit

	def __repr__(self):
		return str(self.__dict__)


class Element():
	'''
	Aids in our Document Type Definition model for EDGAR sec documents
	'''
	def __init__(self, tag, has_end_tag, repeats, required, parent):
		self.tag = tag
		self.has_end_tag = has_end_tag
		self.repeats = repeats
		self.required = required
		self.parent = parent

	def get_end_tag_string(self):
		return self.tag.replace('<', '</')

	def __repr__(self):
		parent_tag = 'root'
		if self.parent:
			parent_tag = self.parent.tag

		return '[{0}, {1}, {2}, {3}, {4}]'.format(
			self.tag
			, self.get_end_tag_string() if self.has_end_tag else 'no end tag'
			, 'repeats' if self.repeats else 'not repeating'
			, 'required' if self.required else 'not required'
			, parent_tag)



# create list of elements for document type description
# DTD of the SGML used by EDGAR is in the doc found at docs/, p. 57

sec_document = Element('<SEC-DOCUMENT>', True, False, True, None)
sec_header = Element('<SEC-HEADER>', True, False, True, sec_document)
acceptance_datetime = Element('<ACCEPTANCE-DATETIME>', False, False, True, sec_header)
document = Element('<DOCUMENT>', True, True, True, sec_document)
# children of document
doc_type = Element('<TYPE>', False, False, True, document)
sequence = Element('<SEQUENCE>', False, False, True, document)
filename = Element('<FILENAME>', False, False, True, document)
description = Element('<DESCRIPTION>', False, False, False, document)
doc_text = Element('<TEXT>', True, False, True, document)
# children of doc_text
pdf = Element('<PDF>', True, False, True, doc_text)
xml = Element('<XML>', True, False, True, doc_text)
xbrl = Element('<XBRL>', True, False, True, doc_text)
table = Element('<TABLE>', True, False, True, doc_text)
caption = Element('<CAPTION>', False, False, True, doc_text)
stub = Element('<S>', False, False, True, doc_text)
column = Element('<C>', False, False, True, doc_text)
footnotes_section = Element('<FN>', False, False, True, doc_text)

# commented out elements that we don't need at the moment
EDGAR_DTD_ELEMENTS = [
	sec_document,
		sec_header,
			acceptance_datetime,
		document,
			doc_type,
			sequence,
			filename,
			description,
			doc_text
				# ,pdf
				,xml
				# ,xbrl
				# ,table
				# ,caption
				# ,stub
				# ,column
				# ,footnotes_section
]

# footnotes (commented out - don't need at the moment)
# for i in range(1,99):
# 	EDGAR_DTD_ELEMENTS += [Element('<F'+str(i)+'>', False, False, True, doc_text)]

# EDGAR_DTD_ELEMENTS += [Element('<PAGE>', False, False, True, doc_text)]


def create_dtd(elements):
	'''
	'''
	dtd = {}
	for element in elements:
		dtd[element.tag] = element
	return dtd

# create our DTD
EDGAR_DTD = create_dtd(EDGAR_DTD_ELEMENTS)
#print(EDGAR_DTD)


def process_document(data):
	'''
	Consumes an SGML document and returns a json/dictionary using recursion

	No python library to parse SGML and solution in 
	https://stackoverflow.com/questions/12505419/parse-sgml-with-open-arbitrary-tags-in-python-3/12534420#12534420
	is a bit complicated

	Need to parse manually using EDGAR DTD
		data is the SGML text

	Approach is recursive (divide and conquer):
	1. find tag that's part of EDGAR's DTD
	2. If no end tag, extract data until next tag
	   Else (has an end tag), 
	       If the enclosed data contains child tags for the
	       given tag, as per the DTD, recurse over enclosed data
	       Else extract the enclosed data
	3. If there is additional data outside of what's enclosed, recurse over that
	   as well
	'''
	data = data.strip()

	result = {}

	tag = get_next_tag(data)
	# print('tag: '+tag)
	# print('data: '+data)
	# print('')
	tag_start = data.find(tag)
	tag_end = tag_start+len(tag)

	if tag in EDGAR_DTD:
		element = EDGAR_DTD[tag]
		value = None
		end = len(data)

		if not element.has_end_tag:
			# extract data until next tag
			next_tag = get_next_tag(data[tag_end:])
			next_tag_start = len(data) # using data since this is used in end
			if next_tag is not None:
				next_tag_start = data.find(next_tag)
			value = data[tag_end:next_tag_start].strip()
			add_result(result, tag, value)
			end = next_tag_start
		else:
			# has an end tag
			end_tag = element.get_end_tag_string()
			end_tag_start = data.find(end_tag)
			enclosed_data = data[tag_end:end_tag_start]
			contains_edgar_tags = False
			children = get_all_children(tag)

			for child in children:
				if child in enclosed_data:
					contains_edgar_tags = True
					break

			if contains_edgar_tags:
				# has children, recurse over enclosed data
				# print('recursing over tag '+tag)
				value = process_document(enclosed_data)
				# print('done recursing over tag '+tag)
				add_result(result, tag, value)
				
				end = end_tag_start + len(end_tag)
			else:
				# no children, extract the enclosed data
				value = enclosed_data.strip()
				add_result(result, tag, value)

				
		if end < len(data):
			# there is additional data outside of what's enclosed, recurse
			additional_data = data[end:]
			# print('recursing over additional data for tag '+tag)
			value = process_document(additional_data)
			# print('done recursing over additional data for tag '+tag)
			key = get_next_tag(additional_data)
			# value will be dict, so no key is needed
			add_result(result, None, value)

	return result


def add_result(result, key, value):
	'''
	Helper to update result based on the key and value, according to the EDGAR DTD
	If key is None, assumes value is dict and recurses over value's keys
	'''
	if key is None:
		# value is dict, add its keys to result recursively
		for value_key in value:
			add_result(result, value_key, value[value_key])
	else:
		element = EDGAR_DTD[key]
		if key in result and not element.repeats:
			# for QA...
			print('overriding '+key+':'+str(result[key]))
			print('with '+key+':'+str(value))

		if element.repeats:
			# dealing with a list
			if key not in result:
				if isinstance(value, list):
					# value is already a list, add to result
					# print('creating result['+key+'] = '+str(value))
					result[key] = value
				else:
					# need to cast value as list
					# print('creating result['+key+'] = ['+str(value)+']')
					result[key] = [value]
			else:
				# it's already a list and in result, add to it
				# print('adding result['+key+'] += '+str(value)+'')
				result[key] += value
		else:
			# print('creating result['+key+'] = '+str(value))
			result[key] = value


def get_next_tag(data):
	'''
	Returns the next opening tag within data, or None if not found
	'''
	opening_tag_regex = '<[^/].+?>'
	tag_match = re.search(opening_tag_regex, data) # without "?", would get <a>0</a> instead of just <a>
	tag = None if tag_match is None else tag_match.group(0)
	return tag


def get_all_children(root):
	'''
	Returns a list of all children in the EDGAR_DTD for a given root element
	'''
	children = []
	for tag in EDGAR_DTD:
		element = EDGAR_DTD[tag]
		if element.parent is not None and element.parent.tag == root:
			children += [tag]
	return children


def test_process_document():
	'''
	Helps test result of process_document
	'''
	import json
	text = '<SEC-DOCUMENT>0001104659-18-050552.txt : 20180808\n<SEC-HEADER>0001104659-18-050552.hdr.sgml : 20180808\n<ACCEPTANCE-DATETIME>20180808170227\n</SEC-HEADER>\n<DOCUMENT>\n<TYPE>4\n<SEQUENCE>1\n<FILENAME>a4.xml\n<DESCRIPTION>4\n<TEXT>\n<XML>\nxml test\n</XML>\n</TEXT>\n</DOCUMENT>\n<DOCUMENT>\n<TYPE>EX-24\n<SEQUENCE>2\n<FILENAME>ex-24.htm\n<DESCRIPTION>EX-24\n<TEXT>\nhtml test\n</TEXT>\n</DOCUMENT>\n</SEC-DOCUMENT>'
	#print(text)

	# convert dict result to json
	processed_document = process_document(text)
	json_document = json.dumps(processed_document)
	#print(json_document)
	print(json_document)

#test_process_document()

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

def get_financial_data(financial_html_text):
	source_soup = BeautifulSoup(financial_html_text, 'html.parser')
	report = source_soup.find('table', {'class':'report'})
	rows = report.find_all('tr')

	unit_text = None
	period_units = []
	dates = []
	super_element = None
	super_label = None

	for row_num, row in enumerate(rows):
		# data is combo of table headers and table data
		data = row.find_all('th') + row.find_all('td')
		result = ''

		us_gaap_element = None
		label = None
		numeric_data = []

		get_data = True

		for index, info in enumerate(data):
			info_text = info.get_text().replace('\n', '')
			delimiter = '\t' if index != 0 else ''
			result = result + delimiter + info_text

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
							period_units = period_units + [info_text] # usually months; use regex for #?
					except KeyError:
						period_units = period_units + ['None']
						dates = dates + [info_text]
						get_data = False

				get_data = False

			elif row_num == 1 and 'th' in class_list:
				# second row indicates dates of data to come
				dates = dates + [info_text]
				get_data = False

			elif 'pl' in class_list:
				# pl class indicates the td is the financial label
				# us-gaap namespace element is in the onclick of the anchor tag
				anchor = info.find('a')
				onclick_attr = anchor.attrs['onclick']
				# strip javascript
				us_gaap_element = onclick_attr.replace(
					'top.Show.showAR( this, \'defref_', ''
					).replace('\', window );', '')
				label = info_text

			elif 'nump' in class_list or 'num' in class_list:
				# nump class indicates td has numeric data
				# might need to replace dollar signs, commas, and spaces
				# also, brackets indicate negative value
				numeric_data = numeric_data + [process_financial_value(info_text)]

			elif 'text' in class_list:
				if len(numeric_data) > 0:
					numeric_data = numeric_data + [process_financial_value(info_text)]
				else:
					# super label (abstract - no financial data)
					get_data = False

		if get_data:
			for index, date in enumerate(dates):

				unit = 'Unknown'
				if 'Per' in us_gaap_element and 'Share' in us_gaap_element:
					unit = 'Share'
				elif (('Shares' in us_gaap_element
					and 'shares in billions' in unit_text.lower())
					or '$ in billions' in unit_text.lower()):
					unit = 'Billions'
				elif (('Shares' in us_gaap_element
					and 'shares in millions' in unit_text.lower())
					or '$ in millions' in unit_text.lower()):
					unit = 'Millions'
				elif (('Shares' in us_gaap_element
					and 'shares in thousands' in unit_text.lower())
					or '$ in thousands' in unit_text.lower()):
					unit = 'Thousands'

				value = numeric_data[index]
				financial_info = FinancialInfo(
								us_gaap_element
								,label
								,period_units[index]
								,date
								,value
								,unit
								)
				print(financial_info)
		else:
			print(us_gaap_element)
			print(result)
		print('')

	#print(report)


def process_financial_value(text):
	'''
	Returns float representation of text after stripping special characters
	'''
	is_negative = True if '(' in text else False
	# strip special characters
	amount_text = re.sub('[\(\)$\s,]', '', text)
	amount = None

	try:
		amount = float(amount_text)
	except ValueError:
		print(amount_text+' is not numeric')

	return -amount if is_negative else amount


def get_document_text(sec_document, filename):
	'''
	Return the TEXT of the filename DOCUMENT in the given sec_document
		sec_document is an EDGAR SGML that's been parsed to JSON
		filename is the FILENAME in the DOCUMENT to find
	'''
	for document in sec_document['<SEC-DOCUMENT>']['<DOCUMENT>']:
		if document['<FILENAME>'] == filename:
			return document['<TEXT>']
	return None


def get_filing_summary_xml(sec_document):
	'''
	Return the XML of the FilingSummary.xml DOCUMENT in the given sec_document
		sec_document is an EDGAR SGML that's been parsed to JSON
	'''
	document_text = get_document_text(sec_document, 'FilingSummary.xml')
	return document_text['<XML>']


def get_html_file_name(filing_summary_xml, report_short_name):
	'''
	Return the HtmlFileName (FILENAME) of the Report in FilingSummary.xml
	(filing_summary_xml) with ShortName in lowercase matching report_short_name
	e.g.
	     report_short_name of consolidated statements of income matches
	     CONSOLIDATED STATEMENTS OF INCOME
	'''
	source_soup = BeautifulSoup(filing_summary_xml, 'html.parser')
	reports = source_soup.find_all('report')
	for report in reports:
		short_name = report.find('shortname')
		if short_name is None:
			print('The following report has no ShortName element')
			print(report)
			continue
		# otherwise, get the text and keep procesing
		short_name = short_name.get_text().lower()
		# we want to make sure it matches, up until the end of the text
		if short_name == report_short_name:
			filename = report.find('htmlfilename').get_text()
			return filename
	print('could not find anything for ShortName '+report_short_name)
	return None


def get_statement_file_names(filing_summary_xml):
	'''
	Return a list of filenames for STATEMENT_SHORT_NAMES in filing_summary_xml:
	'''
	statement_filenames = []
	for short_name in STATEMENT_SHORT_NAMES:
		filename = get_html_file_name(filing_summary_xml, short_name)
		if filename is not None:
			statement_filenames += [filename]

	return statement_filenames


def process_financial_data(sgml_text):
	'''
	Takes sgml_text (from filing url) and extracts the financial data
	Used for processing 10-Q and 10-K documents
	'''
	sec_document = process_document(sgml_text)
	filing_summary_xml = get_filing_summary_xml(sec_document)
	# will change to use for loop on STATEMENT_SHORT_NAMES
	report_short_name = 'consolidated statements of operations'
	filename = get_html_file_name(filing_summary_xml, report_short_name)
	financial_html_text = get_document_text(sec_document, filename)
	get_financial_data(financial_html_text)


