from sgml import *

def test_process_document():
	'''
	Helps test result of process_document
	'''
	import json
	text = '<SEC-DOCUMENT>0001104659-18-050552.txt : 20180808\n<SEC-HEADER>0001104659-18-050552.hdr.sgml : 20180808\n<ACCEPTANCE-DATETIME>20180808170227\n</SEC-HEADER>\n<DOCUMENT>\n<TYPE>4\n<SEQUENCE>1\n<FILENAME>a4.xml\n<DESCRIPTION>4\n<TEXT>\n<XML>\nxml test\n</XML>\n</TEXT>\n</DOCUMENT>\n<DOCUMENT>\n<TYPE>EX-24\n<SEQUENCE>2\n<FILENAME>ex-24.htm\n<DESCRIPTION>EX-24\n<TEXT>\nhtml test\n</TEXT>\n</DOCUMENT>\n</SEC-DOCUMENT>'
	#print(text)

	# convert dict result to json
	processed_document = process_document(text)
	json_document = json.dumps(processed_document)
	#print(json_document)
	print(json_document)

test_process_document()