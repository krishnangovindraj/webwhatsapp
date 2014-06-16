'''
	Core
'''
from Yowsup.connectionmanager import YowsupConnectionManager
from Config import Config,Constants
from WWMException import WWMException

import MySQLdb,time, os, hashlib
class WWMCore:
	def __init__(self):
		
		connectionManager = YowsupConnectionManager()
		connectionManager.setAutoPong(Config.keepAlive)

		self.signalsInterface = connectionManager.getSignalsInterface()
		self.methodsInterface = connectionManager.getMethodsInterface()
		
		self.cm = connectionManager
		
		self.listener = None
		self.sender	= None
		self.session = None
		self.httpRequestHandler = None
		self.instanceId = None
		
		
		self.dbi = None #Do not connect yet
		self.dbiCursor = None
		
		self.yowsupRunning = 0
	
	#Just to keep track of the instances created
	def registerInstance(self, procId):
		timeNow = time.time()
		procId = os.getpid()
		status = Constants.INSTANCESTATUS_STARTED
		authStatus = Constants.AUTHSTATUS_IDLE
		self.dbiCursor.execute("INSERT INTO pythoninstances (userId, procId, lastUpdated,status, authStatus) VALUES(%s, %s, %s, %s)", (self.session.userId, procId, timeNow, status,authStatus))
		#self.instanceId = 

	def genAESKey(self, str):
		#md5 hash of reverse of str
		return hashlib.md5(str[::-1]).hexdigest()
	
		
	def initSender(self):
		self.yowsupRunning = 1
		self.listener = Listener(self)
		
	def initListener(self):
		self.yowsupRunning = 1
		self.sender = Sender(self)
	
	def initDBI(self):
		try:
			self.dbi = MySQLdb.connect('localhost','root','','webwhatsapp')
			self.dbiCursor = self.dbi.cursor(MySQLdb.cursors.DictCursor)
		except MySQLdb.Error e:
			raise WWMException("MySQL could not connect: %s", %e)
		
	def getDBICursor(self):
		if self.dbi == None or self.dbi.open==0:
			self.initDBI()
		
		return self.dbiCursor
	
	#This method is called from session
	def initSession(self, userId, AESKey):
		self.yowsupRunning = 1
		self.session = Session(self, userId, AESKey)
		self.session.login()
	
	def checkStatus():
		self.dbiCursor.execute("SELECT status FROM pythoninstances WHERE instanceId=%s",(self.instanceId,))
		row = self.dbiCursor.fetchone()
		status = row["status"]
	
	def wrapUp(self):
		#Write some code to wrap up
		status = Constants.INSTANCESTATUS_WRAPPEDUP
		self.dbiCursor.execute("UPDATE pythonInstances  set status=%s WHERE instanceId=%s ", (status, self.instanceId))
		
		self.yowsupRunning = 0
		
	def addUser(self, phone,email,name,password,whatsapp_pass):
		AESKey = self.genAESKey(password)
		hash = hashlib.md5(password).hexdigest()
		try:
			db = self.getDBICursor()
			db.execute( "INSERT INTO users (phone,email,name,password,whatsapp_pass) VALUES(%s,%s,%s,%s,AES_ENCRYPT(%s,%s))", (phone, email,name,hash,whatsapp_pass,AESKey) ) 
		except MySQLdb.Error, e:
			print "Exception: %s"%e 	
			#if self.dbi.error:				raise WWMException("DB Error:%s"  db.error) 
		print "Executed but nothing doing"
		