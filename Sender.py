'''
	Sender
'''

import Queue

class Sender:
	def __init__(self,coreRef):
		self.core = coreRef
		if Config.waitForReceipt:
			self.signalsInterface.registerListener("receipt_messageSent", self.onMessageSent)
			self.gotReceipt = False
		
		self.lastReadPending = 0	#To make sure we don't read pending messages twice
		self.retryQueue= Queue.Queue()	#50 messages is pushing it
		self.priority = Queue.Queue()	#50 messages is pushing it


	def getPendingMessages(self):
		resetTimedout()
		self.core.dbiCursor.execute("SELECT * FROM outbox WHERE userId=%s AND sent=%s", (self.core.session.userId, 0))
		while (message = self.core.dbicursor.fetchone()):
			pendingQueue.put(message)
		return self.core.dbicursor.rowcount
		#send them?
	
	def processRetryQueue(self):
		while self.retryQueue.qsize()>0:	#They say some whack shit about this not being reliable in the documentation. Python -_-
			message = self.retryQueue.get():
			sendMessage(message)

	def sendMessage(self, message):
		#if self.core.isConnected == True:
		toJid = "%s@s.whatsapp.net" %message.to
		messageId = self.methodsInterface.call("message_send", (toJid, message.text))
		message.messageId = messageId
		self.logOutgoingMessage(message,Constants.OUTBOX_SENDING)

	def onMessageSent(self, jid, messageId):
		updateMessageStatus(message, Constants.OUTBOX_SENT)
	
	def logOutgoingMessage(self,message):
		self.core.dbiCursor.execute("INSERT INTO outbox (sender,recipient,message,messageId)=%s WHERE messageId=%s", ( message.sender, message.recipient,message.message, message.messageId) )
	
	def updateMessageStatus(self,message, status):
		self.core.dbiCursor.execute("UPDATE outbox SET status=%s WHERE messageId=%s", ( status, message.messageId) )

	def resendTimedOut(self):
		#Reset the ones that have timedout so we can send them again... Assume they failed
		timeNow = time.time()
		treshold = timeNow - Config.OUTBOX_SENDTIMEOUT
		
		self.core.dbiCursor.execute("SELECT sender,recipient,message FROM outbox WHERE status=%s AND lastUpdated<%s", (OUTBOX_SENDING, treshold) )
		pending = self.core.dbiCursor.fetchall()
		for message in pending:
			self.pendingQueue.put(message)
		
		self.core.dbiCursor.execute("UPDATE outbox SET lastUpdated=%s WHERE status=%s AND lastUpdated<%s", (timeNow, OUTBOX_SENDING, treshold) )
		