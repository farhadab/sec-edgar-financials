#EDGAR Filing Predictor
Uses EDGAR Filings for a company to predict stock price using machine learning

Notes:
Come up with machine learning approach to perform EDGAR document analysis. Show what's possible with some structure. Can use SEDAR for machine learning/natural language processing. Could use https://iextrading.com/developer/docs/#financials, but there's some bugs (e.g. https://github.com/iexg/IEX-API/issues/467)
https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm

Daily index provides information on daily filings. 
Full indexes offer a "bridge" between quarterly and daily indexes, compiling filings from the beginning of the current quarter through the previous business day. At the end of the quarter, the full index is rolled into a static quarterly index.
https://www.sec.gov/Archives/edgar/full-index/index.json


What's the hypothesis???
Want to take the price at the close of the filing date vs the closing price the day before and see if the results of the filing