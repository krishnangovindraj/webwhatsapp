#RequestHandler.py

from Core import WWMCore
from Skin import Skin
from Config import Config,Constants
import urlparse,hashlib, time, os


class RequestHandler:
	
	
	def __init__(self):
		self.core = WWMCore()
		self.error = ""
		self.headers = []
		self.environ = None
		self.HTTPsession = None
		self.get = None
		self.post = None
		self.path = ""
		self.response = ""
		self.responseCode = "500 Internal Server Error"
		#No clue what this does
		self.httpd = None
		self.shutdownThread = None
	
	def setShutdownThread(self, httpdRef, sdThread):
		self.httpd = httpdRef
		self.shutdownThread = sdThread
	
	def shutdown(self):	#CANNOT BE CALLED DIRECTLY. TO DO THIS, CALL self.startShutdownSequence()
		timeRemaining = 6
		print "\nShutting down in "
		while timeRemaining>0:
			time.sleep(1)
			timeRemaining = timeRemaining-1
			print "%d...\n"%(timeRemaining)
		
		print "\nbye :)"
		self.httpd.shutdown()
	
	def startShutdownSequence(self): #because sequence sounds badass
		print "Starting shutdown sequence!"
		self.shutdownThread.start()
	
	def requestHandler(self, environ, start_response):
		
		self.environ = environ
		
		self.HTTPSession = environ['beaker.session']	
		self.HTTPSession.save()
		
		self.path = environ["PATH_INFO"][1:]
		self.requestMethod = environ["REQUEST_METHOD"]
		self.queryString = environ["QUERY_STRING"]
		
		self.get = urlparse.parse_qs(self.queryString)
		self.parsePost()
		self.response =""
		
		if self.path=="static":
			self.static()
			start_response(self.responseCode, self.headers)
			return self.response
		
		
		#dummyCursor = self.core.dbi.getCursor()
		
		if self.HTTPSession.get("phone",False) == False:
			#print "Session not set"
			if self.path == "index" or self.path == "":
				self.index()
			else:
				if self.path == "login":
					self.siteLogin()
				else:
					self.redirect302("index")
		
			#self.core.dbi.done()
			start_response(self.responseCode, self.headers)
			return self.response
		'''
		else:
			print "Session: "
			print self.HTTPSession
		'''
		handler = self.resolveRequest()
		print "\n>Resolved to handler %s\n"% handler.__name__
		handler()
		
		#self.core.dbi.done()
		start_response(self.responseCode, self.headers)
		print self.response
		return self.response
	
	def resolveRequest(self):
		#Stackoverflow's equivalent to switch
		return {
			"inbox": self.inbox,
			"chat": self.chat,
			"send": self.send,
			"logout": self.logout,
			"checkStatus": self.checkStatus,
			"startYowsup": self.startYowsup,
			"wrapUp": self.wrapUp
			#,"shutdown": self.startShutdownSequence	#Testing feature only
			}.get(self.path, self.notFound)
	
	def parsePost(self):		
		# the environment variable CONTENT_LENGTH may be empty or missing
		try:
			request_body_size = int(self.environ.get('CONTENT_LENGTH', 0))
		except (ValueError):
			request_body_size = 0
		
		
		request_body = self.environ['wsgi.input'].read(request_body_size)
		self.post = urlparse.parse_qs(request_body)
	
	def redirect302(self, location):
		self.responseCode = "302 Moved Temporarily"
		self.response = ""
		self.headers.append(("Location",location))
		
	
	def inbox(self):
		self.headers.append(('Content-type','text/html'))
		self.responseCode = "200 OK"
		recipient = self.HTTPSession["phone"]
		print "\n\nINBOX: recipient %s"%recipient
		dbiCursor = self.core.dbi.getCursor()
		dbiCursor.execute("SELECT DISTINCT sender,tstamp, 1 AS isunread FROM inbox WHERE recipient=%s AND seen=0 UNION SELECT DISTINCT sender, tstamp,0 AS isunread FROM inbox WHERE recipient=%s AND seen=1 ORDER BY isunread DESC, tstamp DESC",(recipient,recipient))
		convos = dbiCursor.fetchall()
		self.core.dbi.done()
		
		print convos
		self.response = Skin.inbox(convos)
		print "OUT OF INBOX"
	
	def chat(self):
		self.headers.append(('Content-type','text/html'))
		self.responseCode = "200 OK"
		otherperson = self.get.get("with")[0]
		me = self.HTTPSession.get("phone")
		'''
		if otherperson==False:
			self.response = "No messages from that person found"
		else:'''
		dbiCursor = self.core.dbi.getCursor()
		dbiCursor.execute("SELECT * FROM inbox WHERE sender=%s AND recipient=%s AND seen=0 ORDER BY tstamp DESC LIMIT 20", (otherperson,me))
		rec = dbiCursor.fetchall()
		recCount=dbiCursor.rowcount
		if recCount>0:
			getafter = rec[recCount-1]["tstamp"]
			dbiCursor.execute("SELECT *,1 as seen FROM outbox WHERE sender=%s AND recipient=%s AND tstamp>%s ORDER BY tstamp DESC ", (me, otherperson,getafter))
		else:
			dbiCursor.execute("SELECT *,1 as seen FROM outbox WHERE sender=%s AND recipient=%s ORDER BY tstamp LIMIT 20", (me, otherperson,getafter))
		sent = dbiCursor.fetchall()
		
		self.response = Skin.chat(otherperson,sent,rec)
		self.core.dbi.done()
	
	def send(self):
		if self.requestMethod!="POST":
			self.responseCode= "400 Bad Request"	#Should actually be 405
			self.response = "This page can be accessed by POST only"
		
		
		self.headers.append(('Content-type','text/html'))
		self.responseCode = "200 OK"
		
		if self.core.yowsupStarted==0:
			self.response = "Yowsup has not been started. Can't send messages till it has. <a href='/startYowsup'>Start Yowsup</a>"
			return
		
		phonearg = self.HTTPSession["phone"]
		messagearg = self.post.get("message",None)
		recipientarg = self.post.get("recipient",None)
		if messagearg==None or recipientarg==None or phonearg==None:
			self.response = "Invalid arguments"
		else:
			message = {"recipient":recipientarg[0], "messageText":messagearg[0],"sender":phonearg}
			
			self.core.sender.sendMessage(message)
			self.response = "Sending..."

	def logout(self):
		self.core.wrapUp()
		self.redirect302("/")
		'''
		self.responseCode = "302 Moved Temporarily"
		self.headers.append(("Location","/"))
		#self.response="WISE CHOICE. QUIT WHILE YOU STILL CAN"
		'''
	def notFound(self):
		self.responseCode = "404 Not Found"
		self.response = "Invalid path"
	
	def siteLogin(self):
		self.headers.append(('Content-type','text/html'))
		if self.requestMethod!="POST":
			self.response="This page can only be accessed by POST. Please go back to the index"
		else:
			self.responseCode = "200 OK"
			
			phone= self.post.get("phone")[0]
			password = self.post.get("password")[0]
			hash = hashlib.md5(password).hexdigest()
			
			dbiCursor = self.core.dbi.getCursor()
			dbiCursor.execute( "SELECT phone FROM users WHERE phone=%s AND password=%s", (phone,hash) )
			if dbiCursor.rowcount>0:
				row = dbiCursor.fetchone()
				self.HTTPSession["phone"] = row.get("phone")
				self.HTTPSession["AESKey"] = self.core.genAESKey(password)
				self.response= "SUCCESS! <a href='startYowsup'>Start yowsup</a>"
			else:
				self.response ="Login failed"
			
			self.core.dbi.done()
	
	def startYowsup(self):
		if self.core.status==Constants.INSTANCESTATUS_RUNNING and self.core.session.authStatus==Constants.AUTHSTATUS_LOGGEDIN:
			self.headers.append(("Location","/inbox"))
			self.responseCode ="302 Moved Temporarily"
			return
		
		s= self.HTTPSession
		if s["phone"]==None or s["AESKey"]==None:
			self.badRequest()
			return
		else:
			self.core.initListener()
			self.core.initSender()
			self.core.initSession(self.HTTPSession["phone"], self.HTTPSession["AESKey"])
			
			timeToSleep = 3
			while self.core.session.authStatus!=Constants.AUTHSTATUS_LOGGEDIN and self.core.session.authStatus!=Constants.AUTHSTATUS_IDLE and timeToSleep>0:
				time.sleep(1)
				timeToSleep = timeToSleep-1
			
			
			if self.core.session.authStatus == Constants.AUTHSTATUS_LOGGEDIN:
				self.response = "Logged in successfully. Proceed to <a href='/inbox'>inbox</a>"
			else:
				if self.core.session.authStatus == Constants.AUTHSTATUS_IDLE:
					self.response = "Looks like it failed. Try again in some time?"
				else:
					self.response = "Logging in is taking longer than usual. Proceed to<a href='/checkStatus'>Check status to see status.</a>"
	
	def checkStatus(self):
		status = self.core.getStatus()
		
		self.response+= "<h2>Session:</h2><ul>"
		for key,value in status["Session"]:
			self.response+= "<li>%s: %s</li>"%(key,value)
		self.response+="</ul>"
		
		'''for heading,members in status:
			self.response+="\n\n%s:"%(heading)
			for key,value in members:
				self.response+= "\t%s: %s\n"%(key,value)
		'''
	
	def index(self):
		self.responseCode="200 OK"
		if self.HTTPSession.get("phone",False)!=False:
			self.response = Skin.index()
		else:
			self.response = Skin.loginForm()
	
	def wrapUp(self):
		self.responseCode="200 OK"

		if self.requestMethod=="POST":
			confirm = self.post.get("confirmWrapUp",False)
			if confirm:
				self.core.wrapUp("User requested wrap up")
				self.response = Skin.completeHTML("Wrapped up.")
				self.core.dbi.close()
				#self.startShutdownSequence() #if you want to shutdown after this.
		else:
			self.response = Skin.confirmWrapUpForm()
	
	def static(self):
		filearg = self.get.get("file")
		if filearg!=None:
			filepath = "static\%s"%filearg[0]
		else:
			filepath=None
		
		if filepath==None or not os.path.exists(filepath):
			self.responseCode = "404 Not Found"
			self.response = "File could not be found"
		else:
			self.responseCode = "200 OK"
			f=open(filepath, "r")
			self.response = f.read()
	
	def badRequest(self):
		self.responseCode = "400 Bad Request"
		self.response = "Bad request"
