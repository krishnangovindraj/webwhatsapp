
class Skin:
	@staticmethod
	def completeHTML(body):
		html = """
		<html>
			<head>
				<link rel="" href="">
			</head>
			<body>
				%s
			</body>
		</html>
		"""% body
		
		return html
	
	@staticmethod
	def inbox(convos):
		body = "<h2>Inbox</h2>"
		for convo in convos:
			
			if convo.isunread:
				unreadstr = "isunread" 
			else:
				unreadstr = ""
				
			body+="""<div class="inboxconvo %s">
				<a href="/chat?with=%s">%s </a>
				</div>"""% unreadstr, convo.sender, convo.sender
		
		
		return Skin.completeHTML(body)
	
	@staticmethod
	def chat(otherPerson, messages):
		body = "Chat with %s" %otherPerson
		for message in messages:
			if  message.sender==otherPerson:
				cssclass = "chat_received"
				
				if message.seen==0:
					cssclass+=" unread"
			else:
				cssclass = "chat_sent"
			
			
			timestr = message.tstamp
			body+="""
			<div class="%s">
				<span class="timestr">%s</span>
				%s
			</div>"""% cssclass,timestr,messages.message
		
		body+=Skin.sendForm(otherPerson)
		return Skin.completeHTML(body)
	
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
		return Skin.completeHTML(form)

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
		return Skin.completeHTML()
