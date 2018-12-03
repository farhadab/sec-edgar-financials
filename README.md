#SEC EDGAR Financial Reports
Extract financial data from the SEC's EDGAR database.

## Intro
The purpose of this project is to allow users to conveniently extract financial data from the SEC's EDGAR database. This library parses the financial data from the SGML into JSON format. This seamless conversion of filing data to application-ready data is what differentiates this library from other EDGAR libraries.

While it is essentially a web-scraper, the EDGAR filing structure that it is built on, and the formatting of the filings themselves, should remain rather static.


## Example Usage

The below example shows a basic usage of this package.
```python
from edgar.filings.stock import Stock

period = 'quarterly' # or 'annual', which is the default for Stock()
# e.g. the next line will give you just the latest annual results
# stock = Stock('AAPL')
year = 2016
quarter = 1 # 1, 2, 3, or 4
stock = Stock(symbol='AAPL', period=period, year=year, quarter=quarter)
stock.get_statements_of_income()
stock.get_balance_sheets()
stock.get_cash_flows()
```

An example of the output for the statements of income is shown below.
```json
{
	"company": "AAPL",
	"reports": [
		{
			"date": "Dec. 26, 2015",
			"months": 3,
			"map": {
				"us-gaap_SalesRevenueNet": {
					"label": "Net sales",
					"value": 75872000000
				},
				...
			}
		},
		...
	]
}
```

A giving financial statement report will actually contain `reports` for multiple periods/dates. The `map` in each one of these reports contains XBRL elements (e.g. "SalesRevenueNet"), with their namespace found as a prefix (e.g. "us-gaap"). More information on XBRL can be found at https://xbrl.us/data-rule/dqc_0015-le/.

## Terminology
US companies are required by law to file forms with the SEC and these submissions are stored in the EDGAR file system (database), which is organized by year and then by quarter. Below is the terminology we use to navigate the data available to us in this database.

 * `FilingInfo`: Each directory in the file system has an index that keeps track of the location of the filings for all companies that submitted during the period, allowing users to navigate to the file they need.
 * `Filing`: Refers to the text file that the company submits to the SEC, which contains the reported data in SGML format. AKA "SEC filing/document".
   * `DTD`: SEC documents follow a Document Type Definition that describes their SGML structure.
 * `Document` Filings contain one or more Documents, which contain the report data in a number of potential formats (pdf, xml, xbrl, etc.)
   * Documents can have different form types such as 8-K, 10-Q, 10-K, etc.
   * 10-Q and 10-K forms are `financials` that are processed into their income statement, balance sheet, and statement of cash flow components.


## Data
EDGAR doesn't categorize using stock symbols, since not all companies are publicly traded, but rather by a cik value. Can build cik-to-symbol database by running `python -m edgar.data.symbols`. It will append to what's already in place in `symbols.csv` (this means new companies will have to be manually added). At this point, however, it's recommended to manually add to this file as needed as 1) it's a very resource intensive process and 2) they way it's currently coded just continues backwards from the last entry (i.e. wouldn't capture new cik/symbol combos that come to be).

## Roadmap
 * Allow statements to be gathered over a period of time (so not just for a given year+quarter)
 * 