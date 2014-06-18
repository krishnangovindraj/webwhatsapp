from Config import Constants
from DBInterface import BlockingDBICursor
import os, datetime

class Skin:
	@staticmethod
	def completeHTML(body,head=""):
		html = """
		<html>
			<head>
				<link rel="stylesheet" type="text/css" href="/static?file=global.css" />
				%s
			</head>
			<body>
				%s
			</body>
		</html>
		"""% (head,body)
		
		return html
	
	@staticmethod
	def showStatus(status):
		statusSummary= ""
		for heading,members in status.iteritems():
			statusSummary+="<h2>%s:</h2><ul>"%(heading)
			for key,value in members:
				statusSummary+= "\t<li>%s: %s</li>"%(key,value)
			statusSummary+= "</ul>"
		return Skin.completeHTML(statusSummary)
	
	@staticmethod
	def inbox(convos):
		print "Skin.inbox:"
		body = "<h2>Inbox</h2>"
		for convo in convos:
			print convo
			if convo["allread"]==0:
				unreadstr = "hasunread" 
				unreadCount = "(%s)"%(convo["unreadcount"])
			else:
				unreadstr = ""
				unreadCount =""
				
			body+="""<div class="inboxconvo %s">
				<a href="/chat?with=%s">%s %s</a>
				</div>"""% (unreadstr, convo["sender"], convo["sender"], unreadCount)
		body+= StatusLight.getStatusDiv()
		
		return Skin.completeHTML(body)
	
	@staticmethod
	def chat(otherPerson, sent,rec):
		body = "<h2>Chat with %s</h2>" %otherPerson
		
		body+="<div class='chat_container'>"
		#Get the most recent received message
		lastReceivedTimestamp = rec[0]["tstamp"]
		
		messages = Skin.chat_merge(sent,rec)
		for message in messages:
			if  int(message["sender"])==int(otherPerson):
				cssclass = "chat received"
				
				if message["seen"]==0:
					cssclass+=" unread"
			else:
				cssclass = "chat outgoing"
				cssclass+= { 
					Constants.OUTBOX_PENDING: " pending",
					Constants.OUTBOX_SENDING: " sending",
					Constants.OUTBOX_SENT: " delivered",
					}.get(message["status"],"")
			
			
			timestr = datetime.datetime.fromtimestamp(int(message["tstamp"])).strftime('%d/%m/%Y | %H:%M:%S')
			body+="""
			<div class="%s">
				<span class="timestamp">%s@%s</span>
				%s
			</div>"""% (cssclass, message["sender"], timestr,message["message"])
		
		body+=Skin.sendForm(otherPerson)
		body+="""</div>
		<!---End chat_message div--->
		"""
		
		queryString= "action=updateLastReadMessage&chatWith=%s&lastReceivedTimestamp=%s"%(otherPerson,lastReceivedTimestamp)
		body+= StatusLight.getStatusDiv(queryString)
		return Skin.completeHTML(body)
	
	@staticmethod
	def compose():
		form = """
			<div class="sendform">
				<form action="send" method="post">
					<p><input type="text" name="recipient" placeholder="To phonenumber"/></p>
					<p>	<textarea name="message" placeholder="message"></textarea> </p>
					<input type="submit" value="send"/>
				</form>
			</div>
		"""
		return Skin.completeHTML(form)
	
	@staticmethod
	def chat_merge(sent,rec):
		convo = []
		
		s=len(sent)-1
		r=len(rec)-1
		while not (r==-1 and s==-1):
			if not s==-1 and (r==-1 or sent[s]["tstamp"] < rec[r]["tstamp"]):
				convo.append(sent[s])
				s=s-1
			else:
				if s==-1 or sent[s]["tstamp"] >= rec[r]["tstamp"]:
					convo.append(rec[r])
					r=r-1
				else:
					print "requestHandler.chat: Merge sequence messed up"
					break
			
		
		return convo
	
	@staticmethod
	def sendForm(recipient):
		form="""
		<div class="sendform">
			<form action="send" method="post">
				<input type="hidden" name="recipient" value="%s"/>
				<textarea name="message" placeholder="Type message here"></textarea>
				<input type="submit" value="Send"/>
			</form>
		</div>
		"""% recipient
		return form
		#return Skin.completeHTML(form)

	@staticmethod
	def loginForm():
		form="""
		<div class="loginform">
			<form action="login" method="post">
				<input type="text" name="phone" placeholder="phone"/>
				<input type="password" name="password" placeholder="password"/>
				<input type="submit" value="Login"/>
			</form>
		</div>
		"""
		return Skin.completeHTML(form)
	
	@staticmethod
	def index():
		body = """
		Hello, I am the index. You seem to have logged in properly. Here are a few links:
		<ul>
			<li><b><a href="/checkStatus">Check Status:</a></b> See the status of the connection to whatsapp</li>
			<li><b><a href="/inbox">Inbox</a></b> Read messages you have</li>
			<li><b><a href="/compose">compose</a></b> Send a message to someone</li>
			<li><b><a href="/startYowsup">start Yoswup</a></b> Start the yowsup library and connect to whatsapp ( do if the status light is red )</li>
			<li><b><a href="/wrapUp">Wrap up</a></b> Stop the yowsup library from listening and close the connection</li>
			
		</ul>
		"""
		
		body+= StatusLight.getStatusDiv()
		return Skin.completeHTML(body)
	
	@staticmethod
	def confirmWrapUpForm():
		form = """
		<form action="" method="post">
			<input type="hidden" name="confirmWrapUp" value="true"/>
			<input type="submit" value="Confirm wrap up"/>
		</form>
		"""
		return Skin.completeHTML(form)
	
	@staticmethod
	def confirmShutdownForm():
		form = """
		<form action="" method="post">
			<input type="hidden" name="confirmShutdown" value="true"/>
			<input type="submit" value="Confirm shutdown"/>
		</form>
		"""
		return Skin.completeHTML(form)
	
	@staticmethod
	def metaRedirect(url, message, time=2):
		meta = """
			 <META http-equiv="refresh" content="%s;URL=/%s"> 
		"""%(time,url)
		return Skin.completeHTML(message, meta)
	
class StatusLight:
	def __init__(self,coreRef,getParams):
		self.core = coreRef
		self.get = getParams
		self.color = "green" if self.core.status == Constants.INSTANCESTATUS_RUNNING else "red"
		self.processAction()
	
	def processAction(self):
		actionarg = self.get.get("action",False)
		if actionarg==False:
			return
		action = actionarg[0]
		
		callFunc = {
			"updateLastReadMessage": self.updatelastReadMessage,
			#"": ,
			}.get(action,False)
		
		if callFunc!=False:
			print "statusLight action resolved to %s"%(callFunc.__name__)
			callFunc()
		
	def updatelastReadMessage(self):
		chatwith=self.get.get("chatWith",False)
		tstamp=self.get.get("lastReceivedTimestamp",False)
		if chatwith==False or tstamp==False:
			return 
		else:
			otherPerson = chatwith[0]
			lastTstamp = tstamp[0]
		
		with BlockingDBICursor(self.core.dbi) as dbiCursor:
			dbiCursor.execute( "UPDATE inbox SET seen=%s WHERE sender=%s AND tstamp<=%s", (1,otherPerson,lastTstamp) )
		
	def getStatusLightImage(self):
		filepath = "static\\%s.png"%(self.color)	
		if os.path.exists(filepath):
			f=open(filepath, "rb") #READ BINARYYY!
			return f.read()
		else:
			return False		
		#Read a green or red light according to connection status
	
	@staticmethod
	def getStatusDiv(queryString=""):
		div = """
			<div class="statustDiv">
				Yowsup connection status: <img src="statusLight?%s"/>
			</div>
			"""%(queryString)
		
		return div
	