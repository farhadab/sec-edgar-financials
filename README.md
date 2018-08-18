#EDGAR Filing Predictor
Uses EDGAR Filings for a company to predict stock price using machine learning

Notes:
Come up with machine learning approach to perform EDGAR document analysis. Show what's possible with some structure. Can use SEDAR for machine learning/natural language processing.
https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm

Daily index provides information on daily filings. 
Full indexes offer a "bridge" between quarterly and daily indexes, compiling filings from the beginning of the current quarter through the previous business day. At the end of the quarter, the full index is rolled into a static quarterly index.
https://www.sec.gov/Archives/edgar/full-index/index.json

filing.process_document() doesn't account for lists
if multiple, save value as list