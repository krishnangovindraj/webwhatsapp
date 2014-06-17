class Skin:
	@staticmethod
	def completeHTML(body):
		html = """
		<html>
			<head>
				<link rel="stylesheet" type="text/css" href="/static?file=global.css" />
			</head>
			<body>
				%s
			</body>
		</html>
		"""% body
		
		return html
	
	@staticmethod
	def inbox(convos):
		print "Skin.inbox:"
		body = "<h2>Inbox</h2>"
		for convo in convos:
			print convo
			if convo["isunread"]:
				unreadstr = "isunread" 
			else:
				unreadstr = ""
				
			body+="""<div class="inboxconvo %s">
				<a href="/chat?with=%s">%s </a>
				</div>"""% (unreadstr, convo["sender"], convo["sender"])
		
		
		return Skin.completeHTML(body)
	
	@staticmethod
	def chat(otherPerson, sent,rec):
		body = "<h2>Chat with %s</h2>" %otherPerson
		
		body+="<div class='chat_container'>"
		messages = Skin.chat_merge(sent,rec)
		for message in messages:
			if  int(message["sender"])==int(otherPerson):
				cssclass = "chat received"
				
				if message["seen"]==0:
					cssclass+=" unread"
			else:
				cssclass = "chat sent"
			
			
			timestr = message["tstamp"]
			body+="""
			<div class="%s">
				<span class="timestamp">%s@%s</span>
				%s
			</div>"""% (cssclass, message["sender"], timestr,message["message"])
		
		body+=Skin.sendForm(otherPerson)
		body+="""</div>
		<!---End chat_message div--->
		"""
		return Skin.completeHTML(body)
	
	@staticmethod
	def chat_merge(sent,rec):
		convo = []
		
		s=len(sent)-1
		r=len(rec)-1
		while not (r==-1 and s==-1):
			print "\n r,s: %s,%s"%(r,s)
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
		body = "Hello, I am the index"
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
	
