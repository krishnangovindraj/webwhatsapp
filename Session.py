'''
	Session
'''
from Config import Config,Constants
from WWMException import WWMException

class Session:
	def __init__(self, coreRef, userId,decKey):
		self.core = coreRef
		self.userId = userId
		self.decryptKey = decKey
		
		self.phone = ''
		self.password = ''
		self.authStatus = Constants.AUTHSTATUS_IDLE
		
		self.authStatus = Constants.AUTHSTATUS_IDLE
		
		self.core.setSession(self)
		
		#Register a few listeners
		self.core.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
		self.core.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
		self.core.signalsInterface.registerListener("disconnected", self.onDisconnected)
		
		
	def login(self):
		self.core.methodsInterface.call("auth_login", (self.phone, self.password))
		self.updateAuthStatus(Constants.AUTHSTATUS_TRYING)
		
	def onAuthSuccess(self, username):
		print("Authed %s" % username)
		self.methodsInterface.call("ready")
		self.updateAuthStatus(Constants.AUTHSTATUS_LOGGEDIN)

	def onAuthFailed(self, username, err):
		print ("Auth Failed! for %s\nReason: %s" %(username,err) )
		self.authStatus = self.LOGIN_IDLE #Reset status so we can try again
		self.updateAuthStatus(Constants.AUTHSTATUS_IDLE,false)
	
	def onDisconnected(self, reason):
		print("Disconnected (%s) because %s" %(self.phone, reason) )
		self.updateAuthStatus(Constants.AUTHSTATUS_IDLE)

	def updateAuthStatus(self, status,updateDB=True):
		self.authStatus = status
		if updateDB:
			self.core.dbiCursor.execute( "UPDATE pythonInstances SET authStatus=%s WHERE userId=%s", (self.authStatus, self.userId ))

	def getAuthData(self):
		self.core.dbiCursor.execute("SELECT userId, phone, AES_DECRYPT(whatsapp_pass, %s) as password FROM users WHERE userId=%s ", (self.decryptKey, self.userId))
		if self.core.dbiCursor.rowcount==0 :
			raise WWMException("Authdata could not be loaded. Rowcount=0")
			
		authData = self.core.dbiCursor.fetchone()
		self.userId = authData["userId"]	
		self.phone = authData["phone"]
		self.password = authData["password"]
