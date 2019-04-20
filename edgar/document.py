from bs4 import BeautifulSoup
from edgar.dtd import DTD
from edgar.document_text import DocumentText

class Document:
    dtd = DTD()
    description = None

    def __init__(self, data):
        self.type = data[self.dtd.doc_type.tag]
        self.sequence = data[self.dtd.sequence.tag]
        self.filename = data[self.dtd.filename.tag]
        try:
            self.description = data[self.dtd.description.tag]
        except KeyError as e:
            # print('Warning: No {} tag'.format(self.dtd.description.tag))
            pass
        self.doc_text = DocumentText(data[self.dtd.doc_text.tag])


    def get_issuer_trading_symbol(self):
        '''
        Return a tuple of the cik and symbol of a company given an xml_soup of
        the xml of their filing (usually in form 4)
        '''
        # remove leading zeroes (can also just keep in, doesn't matter)
        cik = None
        symbol = None
        
        xml_soup = self.doc_text.xml
        if xml_soup is not None:
            cik = xml_soup.find('issuercik').get_text().lstrip('0')
            symbol = xml_soup.find('issuertradingsymbol').get_text()
            print('cik is {0} and symbol is {1}'.format(cik, symbol))
        else:
            print('document does not have xml, cannot determine symbol')

        return cik, symbol