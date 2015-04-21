import datetime
import dateutil.parser as parser
from lxml import etree as ET
import os

def parse(self, timestr, default=None,
          ignoretz=False, tzinfos=None,
          **kwargs):
    return self._parse(timestr, **kwargs)
parser.parser.parse = parse

#nsmap={'eac': "urn:isbn:1-931666-33-4",'xlink':"http://www.w3.org/1999/xlink",'xsi':"http://www.w3.org/2001/XMLSchema-instance"}

curdir = os.getcwd()

for file in os.listdir(curdir):
	if file.endswith("xml"):
		print file
		tree = ET.parse(file)
		#fix arcrole with purl url
		for relation in tree.iter('{urn:isbn:1-931666-33-4}cpfRelation'):
			print relation
			if relation.get('{http://www.w3.org/1999/xlink}arcrole'):
				relation.set('{http://www.w3.org/1999/xlink}arcrole','http://vocab.org/relationship/'+relation.get('{http://www.w3.org/1999/xlink}arcrole'))

		for dTag in ['{urn:isbn:1-931666-33-4}fromDate', '{urn:isbn:1-931666-33-4}toDate', '{urn:isbn:1-931666-33-4}date']:
			for dDate in tree.iter(dTag):
				dstr = ''
				ddd = parser.parser().parse(dDate.text, None, fuzzy = True)
				if ddd.day:
					dstr = str(ddd.year)+'-'+str("%02d" % ddd.month)+'-'+str("%02d" % ddd.day)
				elif ddd.month:
					dstr =  str(ddd.year)+'-'+str("%02d" % ddd.month)
				elif ddd.year:
					dstr = str(ddd.year)
				else:
					print 'Unreadable date: ' + dDate.text
					continue
				dDate.set("standardDate",dstr)

		tree.write("new/" + file, encoding = 'utf-8', method = 'xml', xml_declaration=True)



