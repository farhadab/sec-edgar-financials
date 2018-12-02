#SEC EDGAR Financials

## Purpose
The purpose of this project is to allow users to conveniently capture financial data from the SEC's EDGAR database. This library parses the financial data from the SGML into JSON format. This seamless conversion of filing data to application-ready data is what differentiates this library from other EDGAR libraries.

## Example Usage

```json
{
	"date": "Sep. 30, 2017",
	"months": 12,
	"map": {
		"us-gaap_SalesRevenueNet": {
			"label": "Net sales",
			"value": 229234000000
		},
		...
	}
}
```


## Data
EDGAR doesn't categorize using stock symbols, since not all companies are publicly traded, but rather by a cik value. Can build cik-to-symbol database by running `python -m symbols.symbols`. It will append to what's already in place in symbols.csv (this means new companies will have to be manually added).

## Terminology
US companies are required by law to file forms with the SEC and these submissions are stored in the EDGAR file system (database), which is organized by year and then by quarter. Below is the terminology we use to navigate the data available to us in this database.

 * `FilingIndex`: Each directory in the file system has an index that keeps track of the location of the filings for all companies that submitted during the period, allowing users to navigate to the file they need.
 * `Filing`: Refers to the text file that the company submits to the SEC, which contains the reported data in SGML format. AKA "SEC filing/document".
   * `DTD`: SEC documents follow a Document Type Definition that describes their SGML structure.
 * `Document` Filings contain one or more Documents, which contain the report data in a number of potential formats (pdf, xml, xbrl, etc.)
   * Documents can have different form types such as 8-K, 10-Q, 10-K, etc.


## Archive
Uses EDGAR Filings for a company to predict stock price using machine learning

Notes:
Come up with machine learning approach to perform EDGAR document analysis. Show what's possible with some structure. Can use SEDAR for machine learning/natural language processing. Could use https://iextrading.com/developer/docs/#financials, but there's some bugs (e.g. https://github.com/iexg/IEX-API/issues/467)
https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm

Daily index provides information on daily filings. 
Full indexes offer a "bridge" between quarterly and daily indexes, compiling filings from the beginning of the current quarter through the previous business day. At the end of the quarter, the full index is rolled into a static quarterly index.
https://www.sec.gov/Archives/edgar/full-index/index.json


What's the hypothesis???
Want to take the price at the close of the filing date vs the closing price the day before and see if the results of the filing