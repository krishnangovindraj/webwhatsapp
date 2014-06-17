'''
	Session
'''
from Config import Config,Constants
from WWMException import WWMException
import base64

class Session:
	def __init__(self, coreRef, phoneNum,decKey):
		self.core = coreRef
		#self.userId = userId
		self.decryptKey = decKey
		
		self.phone = phoneNum
		self.password = None
		self.authStatus = Constants.AUTHSTATUS_IDLE
		
		self.authStatus = Constants.AUTHSTATUS_IDLE
		
		#self.core.setSession(self)	#Deprecated. Core takes care of this
		
		#Register a few listeners
		self.core.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
		self.core.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
		self.core.signalsInterface.registerListener("disconnected", self.onDisconnected)
		
		
	def login(self):
		print "Session.login called"
		if self.authStatus == Constants.AUTHSTATUS_IDLE:
			if self.password == None:
				self.getAuthData()
			self.updateAuthStatus(Constants.AUTHSTATUS_TRYING)
			self.core.methodsInterface.call("auth_login", (self.phone, self.password))
			self.updateAuthStatus(Constants.AUTHSTATUS_TRYING,False)
		#else: #do nothing
		
	def onAuthSuccess(self, username):
		print("Authed %s" % username)
		self.core.methodsInterface.call("ready")
		self.core.authCallback(True)
		self.updateAuthStatus(Constants.AUTHSTATUS_LOGGEDIN)

	def onAuthFailed(self, username, err):
		print ("Auth Failed! for %s\nReason: %s" %(username,err) )
		self.authStatus = self.LOGIN_IDLE #Reset status so we can try again
		self.core.authCallback(False)
		self.updateAuthStatus(Constants.AUTHSTATUS_IDLE,false)
	
	def onDisconnected(self, reason):
		print("Disconnected (%s) because %s" %(self.phone, reason) )
		self.updateAuthStatus(Constants.AUTHSTATUS_IDLE)

	def updateAuthStatus(self, status,updateDB=True):
		self.authStatus = status
		return #Let's not mess with the DB now
		if updateDB:
			dbiCursor = self.core.dbi.getCursor()
			dbiCursor.execute( "UPDATE pythonInstances SET authStatus=%s WHERE phone=%s", (self.authStatus, self.phone))
			self.core.dbi.done()

	def getAuthData(self):
		dbiCursor = self.core.dbi.getCursor()
		dbiCursor.execute("SELECT  phone, AES_DECRYPT(whatsapp_pass, %s) as password FROM users WHERE phone=%s ", (self.decryptKey, self.phone))
		rowcount = dbiCursor.rowcount
		self.core.dbi.done()
		
		if rowcount==0 :
			raise WWMException("Authdata could not be loaded. Rowcount=0")
			
		authData = dbiCursor.fetchone()
		self.phone = authData["phone"]
		rawPass = authData["password"]
		self.password = base64.b64decode(bytes(rawPass.encode('utf-8')))
