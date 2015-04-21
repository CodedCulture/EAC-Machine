
from lxml import etree as ET
import xlrd
from datetime import date, datetime
import dateutil.parser as parsedate
import re


namespaces = {'ns':'isbn:1-931666-33-4', 'xlink': 'http://www.w3.org/1999/xlink',  'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
eacNS = '{urn:isbn:1-931666-33-4}'
parser = ET.XMLParser(remove_blank_text=True)

def parse(self, timestr, default=None,
          ignoretz=False, tzinfos=None,
          **kwargs):
    return self._parse(timestr, **kwargs)

parsedate.parser.parse = parse


def extractRecords(wkbkPath, sheetName, type):
	xlData = xlrd.open_workbook(wkbkPath)
	xlSkinnies = xlData.sheet_by_name(sheetName)

	totalRows = xlSkinnies.nrows - 1
	recordsWritten = 0

	for i in range(1, 10):
		skinnyRow = xlSkinnies.row(i)
		#print skinnyRow
		if skinnyRow[0].value == 0:
			createSkinnyXML(skinnyRow, type)
			recordsWritten = recordsWritten + 1

	print recordsWritten

def createSkinnyXML(values, type):
	#create control section with custom information
	base = createBaseXML(values[1].value)
	print values[1].value
	print values
	print base
	root = base.getroot()

	if type == 'corporate':
		root.append(createCDescription(values, type).getroot())
	elif type == 'person':
		root.append(createPDescription(values, type).getroot())
	else:
		print 'Require "corporate" or "person" as second argument'
	
	base.write('new/' + values[1].value + '.xml', encoding = 'utf-8', method = 'xml', xml_declaration=True, pretty_print = True)


def createBaseXML(recordID):
	base = ET.parse('skinnyControl.xml', parser)

	#add recordID. identify element via xpath?
	base.find('.//' + eacNS + 'recordID').text = recordID

	#maintenanceHistory = base.find('maintenanceHistory')
	maintenanceEvent = base.find('.//' + eacNS + 'maintenanceHistory//' + eacNS + 'eventDateTime')
	maintenanceEvent.text = date.today().strftime('%Y %B %d')
	maintenanceEvent.set('standardDate', date.today().isoformat())

	return(base)


def createMaintenanceEvent(agent, event):
	#create base element
	maintenance = ET.Element('maintenanceEvent')

	#add custom event description
	ET.SubElement(maintenance, 'event').text = event

	#add date and standard date
	time = ET.SubElement(maintenance, 'eventDateTime')
	time.text = date.today().strftime('%Y %B %d')
	time.set('standardDate', date.today().isoformat())

	#add agents
	ET.SubElement(maintenance, 'agentType').text = 'computer'
	ET.SubElement(maintenance, 'agent').text = agent
   	
   	return(maintenance)


def createCDescription(values, type):
	#TODO
	return('')


def createPDescription(values, type):
	cpfDescription = ET.parse('skinnyDescription.xml', parser)

	#identity
	cpfDescription.find('./identity/entityType').text = type
	name = cpfDescription.find('./identity/nameEntry')
	if values[2].value != '':
		name.append(createElement('part', values[2].value, 'localType', '100a'))
	if values[3].value == 'lcnaf':
		#uri?
		name.append(createElement('authorizedForm', 'lcnaf'))

	#description
	description = cpfDescription.find('./description')

	#dates
	existDates = description.find('.//dateRange')
	if values[6].value:
		existDates.append(createDateElement('fromDate', values[6].value))
#### rewrite date converter
	if values[7].value:
		existDates.append(createDateElement('toDate', values[7].value))

	#bioghist
	biogHist = description.find('.//biogHist')
	relations = cpfDescription.find('./relations')
	if values[5].value != '':
		biogHist.append(createElement('p', values[5].value))
	if values[8].value == True:
		biogHist.append(createElement('p', 'This person was employed by the American Museum of Natural History'))
		employee = createAMNHRelation(values[11].value)
		if values[13].value != '':
			employee.append(convertDateRange(values[13].value))
		relations.append(employee)
		
	if values[9].value == True:
		biogHist.append(createElement('p', 'This person served as a trustee for the American Museum of Natural History'))
	if values[10].value != '':
		biogHist.append(createElement('p', values[10].value))

	#relations
	


	return(cpfDescription)


def createElement(tag, value = '', attrib = '', attribValue = False):
	element = ET.Element(tag)
	element.text = unicode(value)
	if attribValue:
		element.set(attrib, attribValue)
	return(element)


def createDateElement(tag, value, approxValue = ''):
	element = ET.Element(tag)
	if approxValue != '':
		value = approxValue
	element.text = value
	element.set('standardDate', convertDateString(value))
	return(element)


def convertDateString(date):
	ddd = parsedate.parser().parse(date, None, fuzzy = True)
	print ddd
	if ddd.day:
		dstr = str(ddd.year)+'-'+str("%02d" % ddd.month)+'-'+str("%02d" % ddd.day)
	elif ddd.month:
		dstr =  str(ddd.year)+'-'+str("%02d" % ddd.month)
	elif ddd.year:
		dstr = str(ddd.year)
	else:
		print 'Unreadable date: ' + date
	return(dstr)


def convertDateRange(dateRange):
	rangeMatch = re.search(r'(.*)-(.*)', dateRange)
	if rangeMatch:
		dates = ET.Element('dateRange')
		fromDate = re.search(r'(.*)(\d\d\d\d)', rangeMatch.group(1))
		toDate = re.search(r'(.*)(\d\d\d\d)', rangeMatch.group(2))
		print fromDate, toDate
		if fromDate:
			dates.append(createDateElement('fromDate', fromDate.group(2), rangeMatch.group(1)))
		if toDate:
			dates.append(createDateElement('toDate', toDate.group(2), rangeMatch.group(2)))
		return(dates)

	else:
		openMatch = re.search(r'(.*)(\d\d\d\d)', dateRange)
		if openMatch:
			dates = ET.Element('dateRange')
			fromDate = re.search(r'\d\d\d\d', openMatch.group(2))
			if fromDate:
				dates.append(createDateElement('fromDate', fromDate.group(0), dateRange))
			return(dates)




def createAMNHRelation(dept = ''):
	relationDesc = 'Employed by AMNH'
	if dept != '':
		relationDesc = 'Employed by AMNH in ' + dept
	relation = ET.Element('cpfRelation')
	relation.set('cpfRelationType', 'identity')

	#need xlink namespace
	relation.set('arcrole', 'employedBy')
	relation.set('href', 'http://vocab.org/relationship/employedBy')
	ET.SubElement(relation, 'descriptiveNote').text = relationDesc

	return(relation)


#URI source