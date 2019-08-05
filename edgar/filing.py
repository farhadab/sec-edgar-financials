'''
Logic related to the handling of filings and documents
'''
from edgar.requests_wrapper import GetRequest
from edgar.document import Document
from edgar.sgml import Sgml
from edgar.dtd import DTD
from edgar.financials import get_financial_report
from datetime import datetime


FILING_SUMMARY_FILE = 'FilingSummary.xml'



class Statements:
    # used in parsing financial data; these are the statements we'll be parsing
    # To resolve "could not find anything for ShortName..." error, likely need
    # to add the appropriate ShortName from the FilingSummary.xml here.
    # TODO: perhaps add guessing/best match functionality to limit this list
    income_statements = ['consolidated statements of income',
                    'consolidated statements of operations',
                    'consolidated statement of earnings',
                    'condensed consolidated statements of income (unaudited)',
                    'condensed consolidated statements of income',
                    'condensed consolidated statements of operations (unaudited)',
                    'condensed consolidated statements of operations',
                    'condensed consolidated statement of earnings (unaudited)',
                    'condensed consolidated statement of earnings',
                    'condensed statements of income',
                    'condensed statements of operations',
                    'condensed statements of operations and comprehensive loss'
                    ]
    balance_sheets = ['consolidated balance sheets',
                    'consolidated statement of financial position',
                    'condensed consolidated statement of financial position (current period unaudited)',
                    'condensed consolidated statement of financial position (unaudited)',
                    'condensed consolidated statement of financial position',
                    'condensed consolidated balance sheets (current period unaudited)',
                    'condensed consolidated balance sheets (unaudited)',
                    'condensed consolidated balance sheets',
                    'condensed balance sheets'
                    ]
    cash_flows = ['consolidated statements of cash flows',
                    'condensed consolidated statements of cash flows (unaudited)',
                    'condensed consolidated statements of cash flows',
                    'condensed statements of cash flows'
                    ]

    all_statements = income_statements + balance_sheets + cash_flows



class Filing:

    STATEMENTS = Statements()
    sgml = None


    def __init__(self, url, company=None):
        self.url = url
        # made this company instead of symbol since not all edgar companies are publicly traded
        self.company = company

        response = GetRequest(url).response
        text = response.text
        
        self.text = text

        print('Processing SGML at '+url)
        
        dtd = DTD()
        sgml = Sgml(text, dtd)

        self.sgml = sgml

        # {filename:Document}
        self.documents = {}
        for document_raw in sgml.map[dtd.sec_document.tag][dtd.document.tag]:
            document = Document(document_raw)
            self.documents[document.filename] = document
        
        acceptance_datetime_element = sgml.map[dtd.sec_document.tag][dtd.sec_header.tag][dtd.acceptance_datetime.tag]
        acceptance_datetime_text = acceptance_datetime_element[:8] # YYYYMMDDhhmmss, the rest is junk
        # not concerned with time/timezones
        self.date_filed = datetime.strptime(acceptance_datetime_text, '%Y%m%d')



    def get_financial_data(self):
        '''
        This is mostly just for easy QA to return all financial statements
        in a given file, but the intended workflow is for he user to pick
        the specific statement they want (income, balance, cash flows)
        '''
        return self._get_financial_data(self.STATEMENTS.all_statements, True)



    def _get_financial_data(self, statement_short_names, get_all):
        '''
        Returns financial data used for processing 10-Q and 10-K documents
        '''
        financial_data = []

        for names in self._get_statement(statement_short_names):
            short_name = names[0]
            filename = names[1]
            print('Getting financial data for {0} (filename: {1})'
                .format(short_name, filename))
            financial_html_text = self.documents[filename].doc_text.data

            financial_report = get_financial_report(self.company, self.date_filed, financial_html_text)

            if get_all:
                financial_data.append(financial_report)
            else:
                return financial_report

        return financial_data



    def _get_statement(self, statement_short_names):
        '''
        Return a list of tuples of (short_names, filenames) for
        statement_short_names in filing_summary_xml
        '''
        statement_names = []

        if FILING_SUMMARY_FILE in self.documents:
            filing_summary_doc = self.documents[FILING_SUMMARY_FILE]
            filing_summary_xml = filing_summary_doc.doc_text.xml

            for short_name in statement_short_names:
                filename = self.get_html_file_name(filing_summary_xml, short_name)
                if filename is not None:
                    statement_names += [(short_name, filename)]
        else:
            print('No financial documents in this filing')

        if len(statement_names) == 0:
            print('No financial documents could be found. Likely need to \
            update constants in edgar.filing.Statements.')
            
        return statement_names



    @staticmethod
    def get_html_file_name(filing_summary_xml, report_short_name):
        '''
        Return the HtmlFileName (FILENAME) of the Report in FilingSummary.xml
        (filing_summary_xml) with ShortName in lowercase matching report_short_name
        e.g.
             report_short_name of consolidated statements of income matches
             CONSOLIDATED STATEMENTS OF INCOME
        '''
        reports = filing_summary_xml.find_all('report')
        for report in reports:
            short_name = report.find('shortname')
            if short_name is None:
                print('The following report has no ShortName element')
                print(report)
                continue
            # otherwise, get the text and keep procesing
            short_name = short_name.get_text().lower()
            # we want to make sure it matches, up until the end of the text
            if short_name == report_short_name.lower():
                filename = report.find('htmlfilename').get_text()
                return filename
        print(f'could not find anything for ShortName {report_short_name.lower()}')
        return None



    def get_income_statements(self):
        return self._get_financial_data(self.STATEMENTS.income_statements, False)

    def get_balance_sheets(self):
        return self._get_financial_data(self.STATEMENTS.balance_sheets, False)

    def get_cash_flows(self):
        return self._get_financial_data(self.STATEMENTS.cash_flows, False)