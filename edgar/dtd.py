'''
Used to define the document type definition used for EDGAR Documents
and other configurations to allow us to read them and make use of their data
'''

class DTD():


    class Element:
        '''
        Aids in our Document Type Definition model for EDGAR sec documents
        '''
        def __init__(self, tag, has_end_tag, repeats, required, parent):
            self.tag = tag
            self.has_end_tag = has_end_tag
            self.repeats = repeats
            self.required = required
            self.parent = parent

        def get_end_tag_string(self):
            return self.tag.replace('<', '</')

        def __repr__(self):
            parent_tag = 'root'
            if self.parent:
                parent_tag = self.parent.tag

            return '<Element [{0}, {1}, {2}, {3}, {4}]>'.format(
                self.tag
                , self.get_end_tag_string() if self.has_end_tag else 'no end tag'
                , 'repeats' if self.repeats else 'not repeating'
                , 'required' if self.required else 'not required'
                , parent_tag)


    # DTD of the SGML used by EDGAR is in the doc found at docs/, p. 57
    sec_document = Element('<SEC-DOCUMENT>', True, False, True, None)
    sec_header = Element('<SEC-HEADER>', True, False, True, sec_document)
    acceptance_datetime = Element('<ACCEPTANCE-DATETIME>', False, False, True, sec_header)
    document = Element('<DOCUMENT>', True, True, True, sec_document)
    # children of document
    doc_type = Element('<TYPE>', False, False, True, document)
    sequence = Element('<SEQUENCE>', False, False, True, document)
    filename = Element('<FILENAME>', False, False, True, document)
    description = Element('<DESCRIPTION>', False, False, False, document)
    doc_text = Element('<TEXT>', True, False, True, document)
    # children of doc_text
    pdf = Element('<PDF>', True, False, True, doc_text)
    xml = Element('<XML>', True, False, True, doc_text)
    xbrl = Element('<XBRL>', True, False, True, doc_text)
    table = Element('<TABLE>', True, False, True, doc_text)
    caption = Element('<CAPTION>', False, False, True, doc_text)
    stub = Element('<S>', False, False, True, doc_text)
    column = Element('<C>', False, False, True, doc_text)
    footnotes_section = Element('<FN>', False, False, True, doc_text)

    # create list of elements for document type description

    # commented out elements that we don't need at the moment
    element_list = [
        sec_document,
            sec_header,
                acceptance_datetime,
            document,
                doc_type,
                sequence,
                filename,
                description,
                doc_text
                    # ,pdf
                    ,xml
                    # ,xbrl
                    # ,table
                    # ,caption
                    # ,stub
                    # ,column
                    # ,footnotes_section
    ]

    # footnotes (commented out - don't need at the moment)
    # for i in range(1,99):
    # 	element_list += [Element('<F'+str(i)+'>', False, False, True, doc_text)]

    # element_list += [Element('<PAGE>', False, False, True, doc_text)]


    def __init__(self):


        def create_dtd(elements):
            '''
            '''
            dtd = {}
            for element in elements:
                dtd[element.tag] = element
            return dtd

        # our DTD is stored in a map so that no hard-coding is needed
        # (e.g. can just loop through it)
        self.map = create_dtd(self.element_list)


    def get_all_children(self, root=None):
        '''
        Returns a list of all children in the EDGAR_DTD for a given root element
        '''
        children = []

        for tag in self.map:
            element = self.map[tag]
            if element.parent is not None and element.parent.tag == root:
                children += [tag]

        return children



