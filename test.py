from functions import createSkinnyXML
from functions import extractRecords

testlist = ['status', 'recordId', 'name', 'full name', 'death', 'authorized', 'uri', 'title', 'dob', 'dod', 'staff', 'trustee', 'other', 'dep', 'depid', 'years', 'expedition']

#createSkinnyXML(testlist, 'person')
extractRecords('../../datadev/data/MASTER_amnhPersons_macros.xlsm', 'amnhp_MASTER', 'person')