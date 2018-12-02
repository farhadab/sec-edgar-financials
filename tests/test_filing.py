import pytest
from filings.filing import Filing


def test_get_financial_data():
	url = 'https://www.sec.gov/Archives/edgar/data/320193/000032019317000070/0000320193-17-000070.txt'#filings_10_k[0].url
	# filing.parse_filing_to_json(url)
	filing = Filing(url, 'AAPL')
	filing.get_financial_data()
	print('test')
	assert 1 == 1