
from lxml import etree as ET
import xlrd
from datetime import date, datetime
import re


namespaces = {'ns':'isbn:1-931666-33-4', 'xlink': 'http://www.w3.org/1999/xlink',  'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
eacNS = '{urn:isbn:1-931666-33-4}'
parser = ET.XMLParser(remove_blank_text=True)


def extractRecords(wkbkPath, sheetName):
   xlData = xlrd.open_workbook(wkbkPath)
   xlSkinnies = xlData.sheet_by_name(sheetName)

   totalRows = xlSkinnies.nrows - 1

   for i in range(1, totalRows):
      skinnyRow = xlSkinnies.row(i)
      if skinnyRow[0].value == 0:
         skinnyXML = createSkinnyXML(skinnyRow)
         saveSkinnyXML = '.../out/' + skinnyRow[1].value + '.xml'
         skinnyXML.write(saveSkinnyXML, encoding = 'utf-8', method = 'xml', xml_declaration=True)


def createSkinnyXML(values, type):
	#create control section with custom information
	base = createBaseXML(values[1])
	root = base.getroot()

	if type == 'corporate':
		description = createCDescription(values, type)
		root.append(description.getroot())
	elif type == 'person':
		description = createPDescription(values, type)
		root.append(description.getroot())
	else:
		print 'Require "corporate" or "person" as second argument"
	
	

	base.write('new/' + values[1] + '.xml', encoding = 'utf-8', method = 'xml', xml_declaration=True, pretty_print = True)


def createBaseXML(recordID):
	base = ET.parse('skinnyControl.xml', parser)

	#add recordID. identify element via xpath?
	base.find('.//' + eacNS + 'recordID').text = recordID

	#maintenanceHistory = base.find('maintenanceHistory')
	maintenanceEvent = base.find('.//' + eacNS + 'maintenanceHistory//' + eacNS + 'eventDateTime')
	maintenanceEvent.text = date.today().strftime('%Y %B %d')
	maintenanceEvent.set('standardDate', date.today().isoformat())

	return(base)


def newMaintenanceEvent(agent, event):
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


def createPDescription(values, type):
	#TODO

def createPDescription(values, type):
	cpfDescription = ET.parse('skinnyDescription.xml', parser)

	#identity
	cpfDescription.find('./identity/entityType').text = type
	name = cpfDescription.find('./identity/nameEntry')
	if values[2] != '':
		name.append(createElement('part', values[2], 'localType', '100a'))
	if values[3] != '':
		name.append(createElement('part', values[3], 'localType', '100q'))
	if values[4] != '':
		name.append(createElement('part', values[4], 'localType', '100d'))
	if values[5] != '':
		#uri?
		name.append(createElement('authorizedForm', values[5]))

	#description
	description = cpfDescription.find('./description')

	#dates
	existDates = description.find('.//dateRange')
	if values[8] != '':
		existDates.append(createElement('fromDate', values[8]))
#### rewrite date converter
	if values[9] != '':
		existDates.append(createElement('toDate', values[9]))

	#bioghist
	biogHist = description.find('.//biogHist')
	if values[7] != '':
		biogHist.append(createElement('abstract', values[7]))
	if values[10] == 'TRUE':
		biogHist.append(createElement('p', 'This person was employed by the American Museum of Natural History'))
		
###create cpfRelation for employee, trustee
		#employee = ET.Element('cpfRelation')
		#employee.set('cpfRelationType', 'identity')
		#employee.set('xlink:arcrole', 'employeeOf')
		#employee.set('xlink:href', 'amnh_1')
		#employee.text = 
		
	if values[11] == 'TRUE':
		biogHist.append(createElement('p', 'This person served as a trustee for the American Museum of Natural History'))
	if values[12] != '':
		biogHist.append(createElement('p', values[12]))

	#relations
	relations = cpfDescription.find('./relations')


	return(cpfDescription)


def createElement(tag, value = '', attrib = '', attribValue = False):
	element = ET.Element(tag)
	element.text = value
	if attribValue:
		element.set(attrib, attribValue)
	return(element)


def convertDateString(date):
	data = strip(date)
	dateRange = re.search(date, r'(.+)-(.+)')
	if dateRange:
		#createElement('fromDate',dateRange.group(1), 'standardDate', convertDateString(dateRange.group(1)))
		#createElement('toDate', dateRange.group(2), 'standardDate', convertDateString(dateRange.group(2)))
		return('')
	day = re.search(date, r',')
	if day:
		print datetime.strptime(date, '%B %d, %Y')
		return('')
	month = re.search(date, r'[A-Za-z]+\s\d\d\d\d')
	if month:
		print datetime.strptime(date, '%B %Y')
		return('')
	year = re.search(date, r'\d\d\d\d')
	if year:
		print datetime.strptime(date, '%Y')
		return('')











