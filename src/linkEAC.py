from lxml import etree as ET
import xlrd
import re
import os

#scan all EAC XML files
#parse each file
#create dictionary of IDs and names from entities
#create dictionry of relationships
#add ids to relationships
#create reciprocal relationships
#write back to xml