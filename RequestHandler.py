#RequestHandler.py

from Core import WWMCore
from Skin import Skin, StatusLight
from Config import Config,Constants
import urlparse,hashlib, time, os, mimetypes
from DBInterface import BlockingDBICursor

class RequestHandler:
	
	@staticmethod
	def initializeStatics(httpdRef,sdThread):
		RequestHandler.core = WWMCore()
		RequestHandler.httpd = httpdRef
		RequestHandler.shutdownThread = sdThread
	
	@staticmethod
	def shutdown():	#CANNOT BE CALLED DIRECTLY. TO DO THIS, CALL self.shutdownRequest
		timeRemaining = 4
		print "\nShutting down in "
		while timeRemaining>0:
			time.sleep(1)
			timeRemaining = timeRemaining-1
			print "%d...\n"%(timeRemaining)
		
		RequestHandler.httpd.shutdown()
	
	@staticmethod
	def startShutdownSequence(): #because sequence sounds badass
		print "Starting shutdown sequence!"
		RequestHandler.shutdownThread.start()
	
	@staticmethod
	def handleNewRequest(environ, start_response): #Creates a new RequestHandler instance
		reqHandler = RequestHandler(environ, start_response)
		reqHandler.processRequest()
		start_response(reqHandler.responseCode, reqHandler.headers)
		
		#print reqHandler.response
		return reqHandler.response
	
	'''
	def __init__(self):
		self.error = ""
		self.headers = []
		self.environ = None
		self.HTTPsession = None
		
		self.path = ""
		self.requestMethod=""
		self.queryString = ""
		self.get = None
		self.post = None
		self.response = ""
		self.responseCode = "500 Internal Server Error"
	'''
	
	def __init__(self, environ, start_response):
		self.error = ""
		self.headers = []
		self.environ = environ
		
		#Session
		self.HTTPSession = environ['beaker.session']	
		self.HTTPSession.save()
		
		#path,get,post
		self.path = environ["PATH_INFO"][1:]
		self.requestMethod = environ["REQUEST_METHOD"]
		self.queryString = environ["QUERY_STRING"]
		
		self.get = urlparse.parse_qs(self.queryString)
		self.parsePost()
		self.response =""
		self.responseCode = "500 Internal Server Error"
		
		#RequestHandler.core.dbi.connect()	#Nope, If you do do this, Create a seperate one for each request.
	
	def processRequest(self):
		handler = self.resolveRequest()
		if handler==None:
			print "Request resolved to None, Too bad"
		else:
			print "\n>Resolved to handler %s\n"% handler.__name__
			handler()
		
	
	def resolveRequest(self):
		#Stackoverflow's equivalent to switch
		if self.path=="static":
			return self.static
		
		#First Check if we have a session.
		if self.HTTPSession.get("phone",False) == False:
			#print "Session not set"
			if self.path == "index" or self.path == "":
				return self.index
			else:
				if self.path == "login":
					return self.siteLogin
				else:
					self.redirect302("index")	#Call it yourself
					return None
		
		return {
			""	: self.index,
			"inbox": self.inbox,
			"chat": self.chat,
			"send": self.send,
			"compose":self.compose,
			"logout": self.logout,
			"checkStatus": self.checkStatus,
			"startYowsup": self.startYowsup,
			"wrapUp": self.wrapUp,
			"statusLight":self.statusLight,
			"shutdown": self.shutdownRequest	#P-P-POOOOOOOWEEEEEEEEEER~!
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
		
	
	def statusLight(self):
		statusLight = StatusLight(self.core,self.get)
		
		self.response = statusLight.getStatusLightImage()
		
		if self.response == False:
			self.response = "File not Found"
			self.responseCode = "404 Not found"
		else:
			self.responseCode = "200 OK"
			self.headers.append(('Content-Type','image/jpeg'))
			#contentDisposition = "Attachment;filename=statuslight_%s.png"%(statusLight.color)#			self.headers.append(('Content-Disposition',contentDisposition))
		
	
	def inbox(self):
		self.headers.append(('Content-type','text/html'))
		self.responseCode = "200 OK"
		recipient = self.HTTPSession["phone"]
		#print "\n\nINBOX: recipient %s"%recipient
		with BlockingDBICursor(RequestHandler.core.dbi) as dbiCursor:
			dbiCursor.execute("SELECT sender,MAX(tstamp) AS tstamp, MIN(seen) AS allread, COUNT(seen = 0) as unreadcount FROM inbox WHERE recipient=%s GROUP BY sender ORDER BY allread DESC, tstamp DESC",(recipient))
			convos = dbiCursor.fetchall()
		
		self.response = Skin.inbox(convos)
		
	def chat(self):
		self.headers.append(('Content-type','text/html'))
		self.responseCode = "200 OK"
		otherperson = False if self.get.get("with",False)==False else self.get.get("with")[0]
		me = self.HTTPSession.get("phone")
		
		if otherperson==False:
			self.response = "No messages from that person found"
			return
		with BlockingDBICursor(RequestHandler.core.dbi) as dbiCursor:
			dbiCursor.execute("SELECT * FROM inbox WHERE sender=%s AND recipient=%s ORDER BY tstamp DESC LIMIT 20", (otherperson,me))
			rec = dbiCursor.fetchall()
			recCount=dbiCursor.rowcount
		
			getafter = rec[recCount-1]["tstamp"]
			if recCount>0:
				dbiCursor.execute("SELECT * FROM outbox WHERE sender=%s AND recipient=%s AND tstamp>%s ORDER BY tstamp DESC ", (me, otherperson,getafter))
			else:
				dbiCursor.execute("SELECT * FROM outbox WHERE sender=%s AND recipient=%s ORDER BY tstamp LIMIT 20", (me, otherperson,getafter))
			sent = dbiCursor.fetchall()
		
		self.response = Skin.chat(otherperson,sent,rec)
		RequestHandler.core.dbi.done()
	
	def compose(self):
		self.response = Skin.compose()
	
	def send(self):
		
		self.headers.append(('Content-type','text/html'))
		if self.requestMethod!="POST":
			self.responseCode= "400 Bad Request"	#Should actually be 405
			self.response = "This page can be accessed by POST only"
		
		
		self.responseCode = "200 OK"
		
		if RequestHandler.core.yowsupStarted==0:
			self.response = Skin.completeHTML("Yowsup has not been started. Can't send messages till it has. <a href='/startYowsup'>Start Yowsup</a>")
			return
		
		phone = self.HTTPSession["phone"]
		messagearg = self.post.get("message",None)
		recipientarg = self.post.get("recipient",None)
		if messagearg==None or recipientarg==None or phone==None:
			self.response = "Invalid arguments"
		else:
			recipient = recipientarg[0]
			message = {"recipient":recipient, "messageText":messagearg[0],"sender":phone}
			
			RequestHandler.core.sender.sendMessage(message)
			
			url = 'chat?with=%s'%(recipient)
			self.response = Skin.metaRedirect(url,"Sending... Redirecting you to the chat page.")

	def logout(self):
		RequestHandler.core.wrapUp()
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
			
			with BlockingDBICursor(RequestHandler.core.dbi) as dbiCursor:
				dbiCursor.execute( "SELECT phone FROM users WHERE phone=%s AND password=%s", (phone,hash) )
				if dbiCursor.rowcount>0:
					row = dbiCursor.fetchone()
					self.HTTPSession["phone"] = row.get("phone")
					self.HTTPSession["AESKey"] = RequestHandler.core.genAESKey(password)
					self.response= Skin.completeHTML("SUCCESS! <a href='startYowsup'>Start yowsup</a>")
				else:
					self.response ="Login failed"
				
			RequestHandler.core.dbi.done()
	
	def startYowsup(self):
		if RequestHandler.core.status==Constants.INSTANCESTATUS_RUNNING and RequestHandler.core.session.authStatus==Constants.AUTHSTATUS_LOGGEDIN:
			self.headers.append(("Location","/inbox"))
			self.responseCode ="302 Moved Temporarily"
			return
		
		s= self.HTTPSession
		if s["phone"]==None or s["AESKey"]==None:
			self.badRequest()
			return
		else:
			RequestHandler.core.initListener()
			RequestHandler.core.initSender()
			RequestHandler.core.initSession(self.HTTPSession["phone"], self.HTTPSession["AESKey"])
			
			timeToSleep = 3 #Just so that the callbacks are completed?
			while RequestHandler.core.session.authStatus!=Constants.AUTHSTATUS_LOGGEDIN and RequestHandler.core.session.authStatus!=Constants.AUTHSTATUS_IDLE and timeToSleep>0:
				time.sleep(1)
				timeToSleep = timeToSleep-1
			
			
			if Constants.AUTHSTATUS_LOGGEDIN == RequestHandler.core.session.authStatus:
				self.response = Skin.completeHTML("Logged in successfully. Proceed to <a href='/inbox'>inbox</a>")
			else:
				if Constants.AUTHSTATUS_IDLE == RequestHandler.core.session.authStatus :
					self.response = "Looks like it failed. Try again in some time?"
				else:
					self.response = "Logging in is taking longer than usual. Proceed to<a href='/checkStatus'>Check status to see status.</a>"
	
	def checkStatus(self):
		status = RequestHandler.core.getStatus()
		self.response = Skin.showStatus(status)
		'''
		self.response+= "<h2>Session:</h2><ul>"
		for key,value in status["Session"]:
			self.response+= "<li>%s: %s</li>"%(key,value)
		self.response+="</ul>"
		'''
		
	
	def index(self):
		self.headers.append(('Content-type','text/html'))
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
				RequestHandler.core.wrapUp("User requested wrap up")
				self.response = Skin.completeHTML("Wrapped up.")
				RequestHandler.core.dbi.close()
				#RequestHandler.startShutdownSequence() #if you want to shutdown after this.
		else:
			self.response = Skin.confirmWrapUpForm()
	
	def shutdownRequest(self):
		self.responseCode = "200 OK"
		if RequestHandler.core.status==Constants.INSTANCESTATUS_RUNNING:
			self.response = "The python instance must be wrapped up ( or atleast, Not running )before you can shut it down"
			return
		
		
		if self.requestMethod=="POST":
			confirm = self.post.get("confirmShutdown",False)
			if confirm:
				RequestHandler.startShutdownSequence()
				self.response = Skin.completeHTML("Shutting down. Bye :)")
		else:
			self.response = Skin.confirmShutdownForm()
		
	
	def static(self):
		filearg = self.get.get("file")
		readmodearg = self.get.get("readmode")
		
		filepath = None if filearg==None else "static/%s"%(filearg[0])
		
		readmode = "rb" if (readmodearg!=None and readmodearg[0]=="binary") else "r"
		mimetype,encoding = mimetypes.guess_type(filepath)
		
		self.headers.append(('Content-Type',mimetype))
		
		if filepath==None or not os.path.exists(filepath):
			self.responseCode = "404 Not Found"
			self.response = "File could not be found"
		else:
			self.responseCode = "200 OK"
			f=open(filepath, readmode)
			self.response = f.read()
	
	def badRequest(self):
		self.responseCode = "400 Bad Request"
		self.response = "Bad request"
	
