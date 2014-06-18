'''
	Core
'''
from Yowsup.connectionmanager import YowsupConnectionManager
from Config import Config,Constants
from WWMException import WWMException
from Session import Session
from Sender import Sender
from Listener import Listener
from DBInterface import DBI, BlockingDBICursor
from CallbackDBI import CallbackDBI

import MySQLdb,time, os, hashlib
class WWMCore:
	def __init__(self):
		
		self.connectionManager = YowsupConnectionManager()
		self.connectionManager.setAutoPong(Config.keepAlive)

		self.signalsInterface = self.connectionManager.getSignalsInterface()
		self.methodsInterface = self.connectionManager.getMethodsInterface()
		
		self.yowsupRanOnce = 0
		
		self.listener = None
		self.sender	= None
		self.session = None
		self.httpRequestHandler = None
		self.instanceId = None
		self.status = Constants.INSTANCESTATUS_INITED
		
		self.dbi = DBI() #Use this for HTTP requests only. For every other case, Go ahead and create a different connection for now
		self.callbackDBI = CallbackDBI()	#Extra care for preventing interference
		#self.dbiCursor = None
		self.yowsupStarted = 0
	
	#Just to keep track of the instances created
	def registerInstance(self, procId):
		timeNow = time.time()
		procId = os.getpid()
		status = Constants.INSTANCESTATUS_STARTED
		authStatus = Constants.AUTHSTATUS_IDLE
		self.dbiCursor.execute("INSERT INTO pythoninstances (phone, procId, lastUpdated,status, authStatus) VALUES(%s, %s, %s, %s)", (self.session.phone, procId, timeNow, status,authStatus))
		#self.instanceId = 

	def genAESKey(self, str):
		#md5 hash of reverse of str
		return hashlib.md5(str[::-1]).hexdigest()
	
		
	def initSender(self):
		if self.sender==None:
			self.sender= Sender(self)
		
	def initListener(self):
		if self.listener==None:
			self.listener = Listener(self)
	
	#deprecated
	def initDBI(self):
		print "Call to Core.initDBI which is deprecated"
		'''
		try:
			self.dbi = MySQLdb.connect('localhost','root','','webwhatsapp')
			self.dbiCursor = self.dbi.cursor(MySQLdb.cursors.DictCursor)
		except MySQLdb.Error, e:
			raise WWMException("MySQL could not connect: %s" %e)
		'''
		
	def getDBICursor(self): #returns dbi and cursor
		return self.dbiCursor
	
	#This method is called from session
	def initSession(self, phone, AESKey):
		print "Core.initSession called"
		if self.session == None or self.session.authStatus == Constants.AUTHSTATUS_IDLE:	#self.yowsupStarted==0 and 
			self.yowsupStarted = 1
			if self.session == None:
				self.session = Session(self, phone, AESKey)
				self.session.getAuthData()
				self.signalsInterface.registerListener("disconnected", self.onDisconnected) 
			self.session.login()
		else:
			print "\nPretty sure yowsup is already started."
	
	def authCallback(self,isSuccess):	#Called manually from Session
		if isSuccess:
			self.yowsupRanOnce==1 #Very important flag
			
			#This is done earlier in initSession with the above flag to differentiate between pre auth disco and post auth disco
			#self.signalsInterface.registerListener("disconnected", self.onDisconnected) 
			
			self.status = Constants.INSTANCESTATUS_RUNNING
			self.yowsupStarted=1
		else:
			self.yowsupStarted= 0
	
	def onDisconnected(self, reason):
		print "Core.onDisconnected called"
		
		if self.status==Constants.INSTANCESTATUS_WRAPPEDUP:
			print "Core.onDisconnected: Disconnected and wrapping up"
			return #And die
		
		
		self.yowsupStarted = 0
		self.session.authStatus = Constants.AUTHSTATUS_IDLE
		#self.session.updateAuthStatus(Constants.AUTHSTATUS_IDLE)
		
		
		if self.yowsupRanOnce==0:
			print "Could not connect. Rerun startYowsup to try again"
			return
		
		self.addNotification(self.session.phone, "Yowsup got disconnected. Will retry")
		
		sleepInterval = Config.conRetry_interval
		print "Disconnected because %s"%(reason)
		print "Retrying every %d seconds"%(sleepInterval)
		retryCount=1
		retryMax = Config.conRetry_maxRetry
		
		while self.session.authStatus!=Constants.AUTHSTATUS_LOGGEDIN and  retryCount<=retryMax:
			time.sleep(sleepInterval)
			print "Retry #%d"%(retryCount)
			self.session.login()
			retryCount = retryCount+1
		
		if self.session.authStatus == Constants.AUTHSTATUS_LOGGEDIN:
			print "Re-Logged in successfully!"
		else:
			self.addNotification(self.session.phone, "Could not login. Retries failed. Killing yowsup")
			print "Can't login. Killing yowsup"
			self.connectionManager.disconnect("Login retries failed")
			self.status = Constants.INSTANCESTATUS_IDLE	#So he can try again manually if he wants
	
	def getStatus(self):
		#Create a dictionary and return it
		status = {}
		
		status["Core"] = [("yowsupStarted", self.yowsupStarted), ("instanceStatus", self.status)]
		
		if self.session==None:
			status["Session"]=[("inited","No")]
		else:
			status["Session"]= [("inited","Yes"), ("AuthStatus",self.session.authStatus)]
		
		return status
	
	def addNotification(self, phone, reason):
		#lol
		return
	
	def wrapUp(self, reason):
		#Write some code to wrap up
		self.status = Constants.INSTANCESTATUS_WRAPPEDUP
		
		with BlockingDBICursor(self.dbi) as dbiCursor:
			dbiCursor.execute("UPDATE pythonInstances  set status=%s WHERE instanceId=%s ", (self.status, self.instanceId))
		
		self.connectionManager.disconnect(reason)
		self.yowsupStarted = 0
	
	def addUser(self, phone,email,name,password,whatsapp_pass):
		AESKey = self.genAESKey(password)
		hash = hashlib.md5(password).hexdigest()
		try:
			dbiCursor = self.dbi.getCursor()
			dbiCursor.execute( "INSERT INTO users (phone,email,name,password,whatsapp_pass) VALUES(%s,%s,%s,%s,AES_ENCRYPT(%s,%s))", (phone, email,name,hash,whatsapp_pass,AESKey) ) 
			self.dbi.commit()
			self.dbi.done()
		except MySQLdb.Error, e:
			print "Exception: %s"%e 	
	
