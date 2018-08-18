import requests
import json
import sgml # custom module to handle sgml processing
import filing # custom module to handle edgar filing lists


'''
This file will be used to parse EDGAR filing data

Forms that we'll be concerned with (all forms are listed at
https://www.sec.gov/forms):
	10-Q: quarterly report and financial statements
	10-K: annual report and financial statements
	8-k: important events (commonly filed)
	4: insider trading (gets us the stock symbol (issuerTradingSymbol))
'''




def parse_filing_to_json(url):
	'''
	Return JSON of Form after parsing url (SGML)
	'''
	index = requests.get(url)
	text = index.text
	#print(text)

	# convert dict result to json
	processed_document = sgml.process_document(text)
	json_document = json.dumps(processed_document['<SEC-DOCUMENT>']['<DOCUMENT>'][0]['<TYPE>'])
	#print(json_document)
	return json_document


# filing_headers, filings = filing.get_filings()
# get all 10-K filings
# filings_10_k = filing.get_all_forms(filings, '10-K')
# print(filings_10_k)

url = 'https://www.sec.gov/Archives/edgar/data/1750/0001047469-18-004978.txt'#filings_10_k[0].url
sgml_text = requests.get(url).text
sgml.process_financial_data(sgml_text)

# for filing in filings[:100]:
# 	if filing.form in ['4', '10-K']:
# 		print('Filing: '+str(filing))
# 		#print(parse_filing_to_json(filing.url))

#print(parse_filing_to_json('https://www.sec.gov/Archives/edgar/data/824142/0000824142-18-000081.txt'))
#url = 'https://www.sec.gov/Archives/edgar/data/1548760/0001127602-18-022351.txt'