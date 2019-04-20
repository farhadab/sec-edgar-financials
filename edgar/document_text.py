from bs4 import BeautifulSoup
from edgar.dtd import DTD

class DocumentText:
    dtd = DTD()
    pdf = None
    xml = None
    xbrl = None
    table = None
    caption = None
    stub = None
    column = None
    footnotes_section = None

    def __init__(self, data):
        self.data = data

        if type(data) is dict and self.dtd.pdf.tag in data:
            self.pdf = data[self.dtd.pdf.tag]

        if type(data) is dict and self.dtd.xml.tag in data:
            xml_text = data[self.dtd.xml.tag]
            self.xml = BeautifulSoup(xml_text, 'html.parser')

        if type(data) is dict and self.dtd.xbrl.tag in data:
            self.xbrl = data[self.dtd.xbrl.tag]

        if type(data) is dict and self.dtd.table.tag in data:
            self.table = data[self.dtd.table.tag]

        if type(data) is dict and self.dtd.caption.tag in data:
            self.caption = data[self.dtd.caption.tag]

        if type(data) is dict and self.dtd.stub.tag in data:
            self.stub = data[self.dtd.stub.tag]

        if type(data) is dict and self.dtd.column.tag in data:
            self.column = data[self.dtd.column.tag]

        if type(data) is dict and self.dtd.footnotes_section.tag in data:
            self.footnotes_section = data[self.dtd.footnotes_section.tag]