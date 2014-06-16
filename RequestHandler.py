#RequestHandler.py

from Core import WWMCore
from Skin import Skin
import urlparse,hashlib

class RequestHandler:
	
	validPaths = ["","inbox","send","logout"]
	def __init__(self):
		self.core = WWMCore()
		self.error = ""
		self.headers = []
		self.environ = None
		self.HTTPsession = None
		self.get = None
		self.post = None
		self.path = ""
		self.responseCode = "500 Internal Server Error"
		#No clue what this does

	def requestHandler(self, environ, start_response):
		self.environ = environ
		
		self.HTTPSession = environ['beaker.session']
		
			
		
		self.path = environ["PATH_INFO"][1:]
		self.requestMethod = environ["REQUEST_METHOD"]
		self.queryString = environ["QUERY_STRING"]
		
		self.get = urlparse.parse_qs(self.queryString)
		self.parsePost()
		
		
		if self.HTTPSession.get("phone",False) == False:
			print "Session not set"
			if self.path == "index" or self.path == "":
				self.index()
			else:
				if self.path == "login":
					self.login()
				else:
					self.redirect302("index")
				
			start_response(self.responseCode, self.headers)
			return self.response
		
		handler = self.resolveRequest()
		print "\n>Resolved to handler %s\n"% handler.__name__
		handler()
		
		self.session.save()
		start_response(self.responseCode, self.headers)
		
		return self.response
	
	def resolveRequest(self):
		#Stackoverflow's equivalent to switch
		return {
			"inbox": self.inbox,
			"chat": self.chat,
			"send": self.send,
			"logout": self.logout,
			"startYowsup:": self.startYowsup
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
		recipient = self.core.session.phone
		self.core.dbiCursor.execute("SELECT DISTINCT sender,tstamp, 1 AS isunread FROM inbox WHERE recipient=%s AND seen=0 UNION SELECT DISTINCT sender, tstamp,0 AS isunread FROM inbox WHERE recipient=%s AND seen=1 ORDER BY isunread DESC, tstamp DESC",(recipient,recipient))
		convos = self.core.dbiCursor.fetchAll()
		self.response = Skin.inbox(convos)
	
	def chat(self):
		self.headers.append(('Content-type','text/html'))
		self.responseCode = "200 OK"
		otherperson = self.get.get("with")
		me = self.core.session.phone
		
		if sender==False:
			self.response = "No messages from that person found"
		else:
			self.core.dbiCursor.execute("SELECT * FROM inbox WHERE sender=%s AND recipient=%s AND seen=0 ORDER BY tstamp DESC LIMIT 20", (otherperson,me))
			received = self.core.dbiCursor.fetchall()
			getafter = received[0].tstamp
			self.core.dbiCursor.execute("SELECT *,1 as seen FROM outbox WHERE sender=%s AND recipient=%s AND tstamp>%s ORDER BY tstamp DESC ", (me, otherperson,getafter))
			sent = self.core.dbiCursor.fetchall()
			#convo = Merge(received, sent)
			self.response = Skin.chat(convo)
		
	def send(self):
		self.headers.append(('Content-type','text/html'))
		self.responseCode = "200 OK"
		self.response = "SEND MY REGARDS TO YO MOMMA!"

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
		
		if self.requestMethod!="POST":
			self.response="This page can only be accessed by POST. Please go back to the index"
		else:
			self.responseCode = "200 OK"
			db = self.core.getDBICursor()
			phone, password = self.post.get("phone"), self.post.get("password")
			hash = hashlib.md5(password).hexdigest()
			db.execute( "SELECT phone FROM users WHERE phone=%s AND password=%s", (phone,hash) )
			if db.rowcount>0:
				row = db.fetchone()
				self.HTTPSession["phone"] = row.get("phone")
				self.HTTPSession["AESKey"] = core.genAESKey(password)
				self.response= "SUCCESS!"
			else
				self.response ="Login failed"
	
	def startYowsup(self):
		if self.core.yowsupRunning==1:
			self.headers.append(("Location","/inbox"))
			self.responseCode ="302 Moved Temporarily"
			return
		
		s= self.HTTPSession
		if s.get("userId")==None or s.get("AESKey")==None:
			self.badRequest()
			return
		else:
			self.core.session = Session(self.HTTPSession.userId, self.HTTPSession.AESKey)
	
	def index(self):
		self.responseCode="200 OK"
		if self.HTTPSession.get("phone",False)!=False:
			self.response = Skin.index()
		else:
			self.response = Skin.loginForm()
	
	def badRequest(self):
		self.responseCode = "400 Bad Request"
		self.response = "Bad request"
