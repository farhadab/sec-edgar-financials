'''
This file will be used to parse EDGAR filing data

Forms that we'll be concerned with (all forms are listed at
https://www.sec.gov/forms):
	10-Q: quarterly report and financial statements
	10-K: annual report and financial statements
	8-k: important events (commonly filed)
	4: insider trading (gets us the stock symbol (issuerTradingSymbol))
'''

import requests
import json
from filings.filing import Filing


if __name__ == '__main__':
	forms = ['4'] # e.g. '10-K' or '10-Q'. 3 and 5 can also be used for issuerTradingSymbol (https://www.sec.gov/fast-answers/answersform345htm.html)
	# filing_headers, filings = filing.get_filings(forms=forms)
	# print(filings)

	# url = filings[0].url
	url = 'https://www.sec.gov/Archives/edgar/data/320193/000032019317000070/0000320193-17-000070.txt'#filings_10_k[0].url
	# test colspan https://www.sec.gov/Archives/edgar/data/862861/0001683168-18-003377.txt
	# filing.parse_filing_to_json(url)
	filing = Filing(url, 'AAPL')
	filing.get_financial_data()
	# next we have to store the processed data
	# https://pypi.org/project/mysqlclient/

	# for filing in filings[:100]:
	# 	if filing.form in ['4', '10-K']:
	# 		print('Filing: '+str(filing))
	# 		#print(parse_filing_to_json(filing.url))

	#print(parse_filing_to_json('https://www.sec.gov/Archives/edgar/data/824142/0000824142-18-000081.txt'))
	#url = 'https://www.sec.gov/Archives/edgar/data/1548760/0001127602-18-022351.txt'