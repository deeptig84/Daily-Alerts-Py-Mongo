# Import libraries
import pymongo
import datetime
import json
from bson import json_util
from pymongo import MongoClient
import datetime
import mandrill
import prettytable  as pt
import pytz
from pytz import timezone

def _custom_json_object_hook(dct):
    if "$date" in dct:
        return utc_str_to_datetime(dct["$date"])
    else:
        return json_util.object_hook(dct)

# Define global variables.
client = MongoClient('mongodb://heroku_wx60bphv:t2vu8eolmbrik0uiur0cahva0j@ds027318.mongolab.com:27318/heroku_wx60bphv')
db = client['heroku_wx60bphv']
#client = MongoClient('mongodb://localhost:27017/')
#db = client['find-your-talents-adminn']
collection = db['genius']
list_scan = []
list_counselling = []
tab_scan = pt.PrettyTable(['Name' , 'Email ID' , 'Phone Number', 'Scehedule details'])
tab_counselling =  pt.PrettyTable(['Name' , 'Email ID' , 'Phone Number','Scehedule details'])
scan_message = ''
counselling_message = ''

# Find the date to be compared
date_to_compare_min = datetime.datetime.utcnow().replace(minute=0, hour=0, second=0, microsecond=0) + datetime.timedelta(days=1)
date_to_compare_max = datetime.datetime.utcnow().replace(minute=0, hour=0, second=0, microsecond=0) + datetime.timedelta(days=2)
# print date_to_compare_min, date_to_compare_max

#Fetch the list of users for the scheduled scans criteria
for genius in collection.find( {"$or": [{"scanAppointmentDate": {"$gte": date_to_compare_min}} ,{"scanAppointmentDate": {"lte": date_to_compare_max}}]}, {"_id" : 0, "email" : 1 , "name.first" : 1 , "phoneNumber" : 1 , "scanAppointmentDate" : 1}):
	list_scan.append(genius)  
#print list_scan	
#Fetch the list of users for the scheduled counselling criteria
for genius in collection.find( {"$and": [{"counsellingDate": {"$gte": date_to_compare_min} }, {"counsellingDate": {"lte": date_to_compare_max}}]}, {"_id" : 0, "email" : 1 , "name.first" : 1 , "phoneNumber" : 1 , "counsellingDate": 1}):
	list_counselling.append(genius)  	

#Convert the lists into JSON format	
list_scan = json.loads(json.dumps(list_scan,default=json_util.default),object_hook=json_util.object_hook)
list_counselling = json.loads(json.dumps(list_counselling,default=json_util.default),object_hook=_custom_json_object_hook)
# print list_scan
#Create a table of users for scan
for genius in list_scan:
   row = [ genius["name"]["first"], genius["email"], genius["phoneNumber"] , genius["scanAppointmentDate"].astimezone(timezone('Asia/Calcutta')).strftime('%d-%m-%Y %I:%M:%S %p')]
   tab_scan.add_row(row)
   
#Create a table of users for counselling
for genius in list_counselling:
   row = [ genius["name"]["first"], genius["email"], genius["phoneNumber"] , genius["counsellingDate"].astimezone(timezone('Asia/Calcutta')).strftime('%d-%m-%Y %I:%M:%S %p')]
   tab_counselling.add_row(row)   

#Send email to the consellor for follow up 
email_subject = 'Follow Up with Client scheduled tomorrow'
opening_msg= ''' 
Dear Anurag,
'''
if len(list_scan) > 0 : 
	scan_message ='''Please find below the list of clients with whom you have scheduled scan appointment tomorrow: 
	'''   + tab_scan.get_string()
else:
	scan_message ='''
No Clients found for the scan tomorrow.
	
	'''
if len(list_counselling) > 0 : 
	counselling_message ='''
	
Please find below the list of clients with whom you have scheduled counselling tomorrow: 
	''' +  tab_counselling.get_string()
else:
	counselling_message ='''
	
No Clients found for the counselling tomorrow.
	
	'''	
closing_msg = ''' 
Thanks and Regards,
Find Your Talents - Techies
Wish you a wonderful day ahead.
'''

mandrll_apikey = 'uP9avYSTtIVL4pvpo6erEg'	

email_message = opening_msg + scan_message	+ counselling_message 	+ closing_msg

to_list = [{'email' : 'deeptig84@gmail.com'},{'email' : 'anuraggupta86@gmail.com'},{'email' : 'sagarmeansocean@gmail.com'}   ]

try:
	mandrill_client = mandrill.Mandrill(mandrll_apikey)
	message = {
				 'from_email': 'lsagar.12@gmail.com',
				 'from_name': 'Sagar',
				 'headers': {'Reply-To': 'message.reply@example.com'},
				 'important': False,
				 'subject': email_subject,
				 'text': email_message,
				 'to': to_list,
				 'track_clicks': True,
				 'track_opens': True
			   }
	result = mandrill_client.messages.send(message=message, async=False)
	'''
	[{'_id': 'abc123abc123abc123abc123abc123',
	'email': 'recipient.email@example.com',
	'reject_reason': 'hard-bounce',
	'status': 'sent'}]
	'''
	
	# print result
	# print email_message

except mandrill.Error, e:
	# Mandrill errors are thrown as exceptions
	print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
	# A mandrill error occurred: <class 'mandrill.UnknownSubaccountError'> - No subaccount exists with the id 'customer-123'
	raise