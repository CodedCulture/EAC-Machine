# EAC-Machine
Python scripts for converting EAC-CPF records in Excel documents into XML for the American Museum of Natural History Library

## Usage
from createEAC import extractRecords

extractRecords() takes three arguments
* wkbkPath - location of Excel document
* sheetName - sheet containing data to be converted
* type - whether the entities are people or corporations