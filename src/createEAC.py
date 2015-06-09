from lxml import etree as ET
import xlrd
from datetime import date, datetime
import dateutil.parser as parsedate
import re
from parseDates import parseDates, createDateElement


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

	for value in values:
		if isinstance(value.value, float):
			value.value = str(int(value.value))
		if isinstance(value.value, basestring):
			value.value = value.value.strip(' .,')

	root = base.getroot()

	if type == 'corporate':
		root.append(createCDescription(values, type).getroot())
	elif type == 'person':
		root.append(createPDescription(values, type).getroot())
	else:
		print 'Require "corporate" or "person" as second argument'
	
	base.write('new/' + values[1].value + '.xml', encoding = 'utf-8', method = 'xml', xml_declaration=True, pretty_print = True)


def createBaseXML(recordID):
	base = ET.parse('templates/skinnyControl.xml', parser)

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
	cpfDescription = ET.parse('templates/skinnyDescription.xml', parser)

	#identity
	cpfDescription.find('./identity/entityType').text = type
	names = cpfDescription.find('./identity')
	
	if values[2].value != '':
		names.append(createNameEntry(values[2].value, '110a'))

	if values[3].value != '':
		names.append(createNameEntry(values[4].value, '110a', 'opac'))

	if values[4].value != '':
		names.append(createNameEntry(values[4].value, '110a', 'viaf'))

	#description
	description = cpfDescription.find('./description')

	#dates
	existDates = description.find('.//dateRange')

	if values[6].value:
		existDates.append(createDateElement('fromDate', values[6].value))

	if values[7].value:
		existDates.append(createDateElement('toDate', values[7].value))

	if values[8].value:
		existDates.append(createElement('descriptiveNote', values[8].value))

#TO DO place values

	#bioghist
	biogHist = description.find('.//biogHist')
	relations = cpfDescription.find('./relations')

	if values[10].value != '':
		biogHist.append(createElement('p', values[10].value))

	if values[11].value != '':
		people = values[11].value.split(';')
		for person in people:
			parts = person.split(',')
			if len(parts) == 1:
				name = person
			else:
				name =  parts[1].strip() + ' ' + parts[0].strip()
			if len(parts) == 3:
				desc = 'Served as ' + parts[2]
				relations.append(createRelation(name, desc))
			else:
				relations.append(createRelation(name, 'Expedition staff'))

	if values[12].value != '':
		depts = values[12].value.split(';')
		for dept in depts:
			relations.append(createRelation(dept, 'Organized expedition'))

	if values[13].value != '':
		sponsors = values[13].value.split(';')
		for sponsor in sponsors:
			relations.append(createRelation(sponsor, 'Sponsored expedition'))


#TO DO 14 related resources

#TO DO 15 related publications
	


	return(cpfDescription)


def createPDescription(values, type):
	cpfDescription = ET.parse('skinnyDescription.xml', parser)

	#identity
	cpfDescription.find('./identity/entityType').text = type
	names = cpfDescription.find('./identity')

	if values[2].value != '' & values[3].value == 'lcnaf':
		names.append(createNameEntry(values[2].value, '100a', 'lcnaf'))
	elif values[2].value != '':
		names.append(createNameEntry(values[2].value, '100a'))

	#description
	description = cpfDescription.find('./description')

	#dates
	existDates = description.find('.//dateRange')
	if values[6].value:
		existDates.append(createDateElement('fromDate', values[6].value))

	if values[7].value:
		existDates.append(createDateElement('toDate', values[7].value))

	#bioghist
	biogHist = description.find('.//biogHist')
	relations = cpfDescription.find('./relations')

	if values[5].value != '':
		biogHist.append(createElement('p', values[5].value))

	if values[8].value == True:
		biog = 'This person was employed by the American Museum of Natural History'
		relations.append(createRelation('American Museum of Natural History', 'Employed by AMNH', 'employedBy', values[13].value))

	if values[11].value != '':
		if biog:
			biog = biog[0:-1] + 'in ' + values[11].value + '.'
		else:
			biog = 'This person was employed by the American Museum of Natural History in ' + values[11].value + '.'
		relations.append(createRelation(values[11].value, 'Employed by AMNH in ' + values[11].value, 'employedBy', values[13].value))
		
	if values[9].value == True:
		if biog:
			biog = biog + 'This person also served as a trustee.'
		else:
			biog = 'This person also served as a trustee for the American Museum of Natural History.'
		relations.append(createRelation('American Museum of Natural History', 'Trustee of AMNH', '', values[13].value))

	if biog:
		biogHist.append(createElement('p', 'biog'))

	if values[10].value != '':
		biogHist.append(createElement('p', values[10].value))


	return(cpfDescription)


def createElement(tag, value = '', attrib = '', attribValue = False):
	element = ET.Element(tag)
	element.text = unicode(value)
	if attribValue:
		element.set(attrib, attribValue)
	return(element)


def createNameEntry(name, localType, authority = ''):
	nameEntry = ET.Element('nameEntry')
	nameEntry.append(createElement('part', name, 'localType', localType))
	if authority != '':
		nameEntry.append(createElement('authorizedForm', authority))

	return(nameEntry)


def createRelation(entity, desc, arcrole = '', date = ''):
	relation = ET.Element('cpfRelation')
	relation.set('cpfRelationType', 'identity')

	#need xlink namespace
	if arcrole != '':
		relation.set('arcrole', arcrole)
		relation.set('href', 'http://vocab.org/relationship/' + arcrole)
	ET.SubElement(relation, 'relationEntry').text = entity
	if date != '':
		relation.append(parseDates(date))
	note = ET.SubElement(relation, 'descriptiveNote')
	ET.SubElement(note, 'p').text = desc

	return(relation)

#TODO unicode
#TODO relationship URIs