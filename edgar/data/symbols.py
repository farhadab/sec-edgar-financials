'''
This is used to backload symbols.csv in order to map a cik to a symbol
'''
import pandas as pd
import sys
# to overcome no module found error, use "python -m symbols.symbols"
from edgar.edgar import get_index_json, _get_filing_info, SYMBOLS_DATA_PATH
from edgar.filing import Filing

csv_path = SYMBOLS_DATA_PATH

def get_all_symbols():

    # expects a csv with columns=['cik', 'symbol', 'year', 'quarter', 'filing_url']
    df = pd.read_csv(csv_path, converters={'cik' : str})
    # df.cik = df.cik.astype(str) # was converting to float

    results = df.to_dict('list')

    # dict cik:symbol
    # results = {
    # 	'cik':[],
    # 	'symbol':[],
    # 	'year':[],
    # 	'quarter':[],
    # 	'filing_url':[]
    # }

    starting_year = ''
    starting_quarter = ''
    starting_filing_url = ''

    try:
        starting_year = results['year'][-1]
        starting_quarter = results['quarter'][-1]
        starting_filing_url = results['filing_url'][-1]
    except:
        print('No previous data; starting from scratch')

    # these have issuerTradingSymbol (https://www.sec.gov/fast-answers/answersform345htm.html)
    forms = ['3', '4', '5'] 
                    
    # starts at full index, reverse to focus on most recent symbol data
    full_directory_item_list = reversed(get_index_json()['directory']['item'])
    
    found_starting_year = True if starting_year == '' else False
    found_starting_quarter = True if starting_quarter == '' else False
    found_starting_filing_url = True if starting_filing_url == '' else False

    try:
        for directory_item in full_directory_item_list:
            if directory_item['type'] == 'dir':
                year = directory_item['href']

                if not found_starting_year and year == starting_year:
                    found_starting_year = True

                quarter_directory_item_list = reversed(get_index_json(year=year)['directory']['item'])

                for quarter_directory_item in quarter_directory_item_list:
                    # basically no good/xml data before 2004
                    if quarter_directory_item['type'] == 'dir' \
                    and int(directory_item['name']) >= 2004 \
                    and found_starting_year:
                        quarter = quarter_directory_item['href']

                        if not found_starting_quarter and quarter == starting_quarter:
                            found_starting_quarter = True
                            
                        print('year {0} quarter {1}'.format(year, quarter))
                        
                        filings = _get_filing_info(forms=forms, year=year, quarter=quarter)
                        
                        for filing in filings:
                            filing_url = filing.url

                            if not found_starting_filing_url and filing_url == starting_filing_url:
                                found_starting_filing_url = True

                            # see Accession Number in
                            # https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm
                            # e.g. url: https://www.sec.gov/Archives/edgar/data/filing_cik/0..filing_cik-18-000137.txt
                            # For conglomerates, the ciks in the url may be
                            # different, depending on the entity that actually
                            # files
                            filing_url_list = filing_url.split('/')
                            filing_cik_dir = filing_url_list[6]
                            filing_cik = filing_url_list[7].split('-')[0].lstrip('0')
                            # print(filing_cik)

                            # process only if we haven't seen the cik before
                            # helps with performance
                            if filing_cik_dir not in results['cik'] \
                                and filing_cik not in results['cik'] \
                                and found_starting_quarter \
                                and found_starting_filing_url:
                                cik, symbol = process_symbol_filing(filing_url)
                                
                                # add to results only if it's not already in there
                                # or if the symbol has changed (get most recent)
                                # but this latter condition is handled by reverse
                                if cik not in results['cik'] and cik != '' and cik is not None:
                                    results['cik'] += [cik]
                                    results['symbol'] += [symbol]
                                    results['year'] += [year]
                                    results['quarter'] += [quarter]
                                    results['filing_url'] += [filing_url]
    except Exception as e:
        print(e)
    finally:
        df = pd.DataFrame(results, columns=['cik', 'symbol', 'year', 'quarter', 'filing_url'])
        df = df.set_index('cik')
        df.to_csv(csv_path)



def process_symbol_filing(filing_url):
    '''
    Helper returning a tuple of cik, symbol given a url of a filing that 
    contains an XML document with issuerCik issuerTradingSymbol tags 
    (usually forms 3, 4, or 5)
    '''
    filing = Filing(filing_url) # we don't care about the company here
    document = list(filing.documents.values())[0]
    return document.get_issuer_trading_symbol()


if __name__ == '__main__':
    get_all_symbols()