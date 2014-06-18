#Config and plenty of constants
class Config:
		keepAlive = True
		sendReceipts = False
		#waitForReceipt = False
		
		session_opts = {'session.type': 'file', 'session.cookie_expires': True,'session.file_dir': 'beaker\\file_dir','session.data_dir': 'beaker\\data_dir'}
		
		#CONNECTION
		conRetry_interval= 10 #Retry every 10 seconds
		conRetry_maxRetry = 12 #Retry 12 times
		
		#CallbackDBI
		CallbackDBI_queryTimeout = 3
		
		#Sender
		#Sender_sendtimeout= 90 #1.5 minutes
		Sender_resendInterval = 5#150
		
		#outbox
		outbox_retryInterval = 5#90 #1.5 minutes
		#DBI
		DBI_getCursorTimeout = 20 #20 seconds is a looot
		#mysql connection
		mysql_host= "localhost"
		mysql_user= "root"
		mysql_password= ""
		mysql_database= "webwhatsapp"
		
		

class Constants:		
	#DBI
	DBI_FETCHALL = 1
	DBI_FETCHONE = 2
	DBI_ROWCOUT  = 3
	
	#INBOX
	INBOX_UNSEEN = 1
	INBOX_SEEN = 2
	
	#OUTBOX
	OUTBOX_PENDING = 1
	OUTBOX_SENDING = 2
	OUTBOX_SENT = 3
		
	#AUTH
	AUTHSTATUS_IDLE = 1
	AUTHSTATUS_TRYING = 2
	AUTHSTATUS_LOGGEDIN = 3
	
	
	#INSTANCESTATUS	(Notes the status of the process in the databases. Mostly to keep track of instances
	INSTANCESTATUS_INITED = 0
	INSTANCESTATUS_RUNNING = 1
	INSTANCESTATUS_WRAPPEDUP = 2
