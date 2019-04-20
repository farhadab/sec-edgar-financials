'''
This file will be used to parse the sgml of an SEC document/filing
given a DTD (dtd)
'''
import re


class SgmlException(Exception):
    pass


class Sgml:

    def __init__(self, document, dtd):
        self.dtd = dtd
        self.document = document
        self.map = self._parse_sgml(document)


    def _parse_sgml(self, data) -> dict():
        '''
        Consumes an SGML document and returns a json/dictionary using recursion

        No python library to parse SGML and solution in 
        https://stackoverflow.com/questions/12505419/parse-sgml-with-open-arbitrary-tags-in-python-3/12534420#12534420
        is a bit complicated

        Need to parse manually using EDGAR self.dtd
            data is the SGML text

        Approach is recursive (divide and conquer):
        1. find tag that's part of EDGAR's self.dtd
        2. If no end tag, extract data until next tag
           Else (has an end tag), 
               If the enclosed data contains child tags for the
               given tag, as per the self.dtd, recurse over enclosed data
               Else extract the enclosed data
        3. If there is additional data outside of what's enclosed, recurse over that
           as well
        '''
        data = data.strip()

        result = {}

        try:
            tag = self._get_next_tag(data)
            # print('tag: '+tag)
            # print('data: '+data)
            # print('')

            if tag in self.dtd.map: # also covers the case where tag is None
                tag_start = data.find(tag)
                tag_end = tag_start+len(tag)

                element = self.dtd.map[tag]
                value = None
                end = len(data)

                if not element.has_end_tag:
                    # extract data until next tag
                    next_tag = self._get_next_tag(data[tag_end:])
                    next_tag_start = len(data) # using data since this is used in end
                    if next_tag is not None:
                        # print('next_tag is '+next_tag)
                        next_tag_start = data.find(next_tag)
                    value = data[tag_end:next_tag_start].strip()
                    self._add_result(result, tag, value)
                    end = next_tag_start
                else:
                    # has an end tag
                    end_tag = element.get_end_tag_string()
                    # print('end_tag is '+end_tag)
                    end_tag_start = data.find(end_tag)
                    enclosed_data = data[tag_end:end_tag_start]
                    # print(enclosed_data)
                    contains_edgar_tags = False
                    children = self.dtd.get_all_children(tag)
                    # print(children)

                    for child in children:
                        if child in enclosed_data:
                            contains_edgar_tags = True
                            break
                        else:
                            # the tag isn't in the enclosed_data, so we add empty result
                            child_element = self.dtd.map[child]
                            
                            if child_element.required:
                                child_no_value = [] if child_element.repeats else ''
                                self._add_result(result, child, child_no_value)

                    if contains_edgar_tags:
                        # has children, recurse over enclosed data
                        # print('recursing over tag '+tag)
                        # print(enclosed_data)
                        value = self._parse_sgml(enclosed_data)
                        # print('done recursing over tag '+tag)
                        self._add_result(result, tag, value)
                        
                    else:
                        # no children, extract the enclosed data
                        value = enclosed_data.strip()
                        self._add_result(result, tag, value)

                    end = end_tag_start + len(end_tag)
                        
                if end < len(data):
                    # there is additional data outside of what's enclosed, recurse
                    additional_data = data[end:]
                    # print('recursing over additional data for tag '+tag)
                    # print(additional_data)
                    value = self._parse_sgml(additional_data)
                    # print('done recursing over additional data for tag '+tag)
                    key = self._get_next_tag(additional_data)
                    # value will be dict, so no key is needed
                    self._add_result(result, None, value)

        except KeyError as e:
            raise SgmlException('Could not parse sgml: {}'.format(e))
        
        return result


    def _add_result(self, result, key, value):
        '''
        Helper to update result based on the key and value, according to the EDGAR self.dtd
        If key is None, assumes value is dict and recurses over value's keys
        '''
        if key is None:
            # value is dict, add its keys to result recursively
            for value_key in value:
                self._add_result(result, value_key, value[value_key])
        else:
            element = self.dtd.map[key]
            # print('adding result for '+key)

            if key in result and not element.repeats:
                # for QA...
                print('overriding '+key+':'+str(result[key]))
                print('with '+key+':'+str(value))

            if element.repeats:
                # dealing with a list
                if key not in result:
                    if isinstance(value, list):
                        # value is already a list, add to result
                        # print('creating result['+key+'] = '+str(value))
                        result[key] = value
                    else:
                        # need to cast value as list
                        # print('creating result['+key+'] = ['+str(value)+']')
                        result[key] = [value]
                else:
                    # it's already a list and in result, add to it
                    # print('adding result['+key+'] += '+str(value)+'')
                    result[key] += value
            else:
                # print('creating result['+key+'] = '+str(value))
                result[key] = value


    @staticmethod
    def _get_next_tag(data):
        '''
        Helper to return the next opening tag within data, or None if not found
        '''
        opening_tag_regex = '<[^/].+?>'
        tag_match = re.search(opening_tag_regex, data) # without "?", would get <a>0</a> instead of just <a>
        # print(data)
        # print(tag_match)
        tag = None if tag_match is None else tag_match.group(0)
        return tag