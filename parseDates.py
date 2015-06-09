import datetime
import dateutil.parser as parser
from lxml import etree as ET
import re

def parse(self, timestr, default=None,
          ignoretz=False, tzinfos=None,
          **kwargs):
    return self._parse(timestr, **kwargs)

parser.parser.parse = parse


def parseDates(dateString):
	dateSet = re.search(r',', dateString)

	if dateSet:
		dates = dateString.split('')
		dateElement = ET.Element('dateSet')

		for date in dates:
			dateElement.append(parseDates(date))
	else:
		dateRange = re.search(r'-', dateString)

		if dateRange:
			dateElement = convertDateRange(dateString)
		else:
			dateElement = createDateElement('date', dateString)

	return(dateElement)



def createDateElement(tag, dateString):
	dateElement = ET.Element(tag)

	convertedDateString = convertDateString(dateString)

	value = convertedDateString[0]
	dateElement.text = value
	dateElement.set('standardDate', convertedDateString[1])

	if convertedDateString[2] != '':
		print 'Hi'



	return(dateElement)


def convertDateString(dateString):
	testedDateString = testApproxValue(dateString)
	date = testedDateString[1]

	ddd = parser.parser().parse(date, None, fuzzy = True)
	print ddd

	if ddd.day:
		dstr = str(ddd.year)+'-'+str("%02d" % ddd.month)+'-'+str("%02d" % ddd.day)
	elif ddd.month:
		dstr =  str(ddd.year)+'-'+str("%02d" % ddd.month)
	elif ddd.year:
		dstr = str(ddd.year)
	else:
		print 'Unreadable date: ' + date
		date = input('Enter a new date as (before, after, etc) dd Month yyyy e.g. (after 01 January 2000):')
		dstr = convertDateString(date)

	testedDateString[1] = dstr

	return(testedDateString)


def testApproxValue(dateString):
	justDateString = dateString
	approxString = ''

	approxStrings = re.search(r'(.*)(before|after|\?)(.*)', dateString)

	if approxStrings:
		approxString = approxStrings.group(2)
		if approxStrings.group(1) != '':
			justDateString = approxStrings.group(1)
		else:
			justDateString = approxStrings.group(3)

	return([dateString, justDateString, approxString])


def convertDateRange(dateRange):
	rangeMatch = re.search(r'^(.*)-(.*)$', dateRange)

	dateElement = ET.Element('dateRange')

	if rangeMatch.group(1):
		dateElement.append(createDateElement('fromDate', rangeMatch.group(1)))
	if rangeMatch.group(2):
		dateElement.append(createDateElement('toDate', rangeMatch.group(2)))

	return(dateElement)

