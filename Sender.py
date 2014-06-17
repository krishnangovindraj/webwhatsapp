'''
	Sender
'''

import Queue, time
from Config import Config,Constants
from DBInterface import DBI
class Sender:
	def __init__(self,coreRef):
		print "initing Sender"
		self.core = coreRef
		if Config.waitForReceipt:
			self.signalsInterface.registerListener("receipt_messageSent", self.onMessageSent)
		
		self.lastReadPending = 0	#To make sure we don't read pending messages twice
		self.retryQueue= Queue.Queue()	#50 messages is pushing it
		self.priority = Queue.Queue()	#50 messages is pushing it
		self.queueDBI = DBI()

	def getPendingMessages(self):
		resetTimedout()
		dbiCursor = self.core.dbi.getDBICursor()
		dbiCursor.execute("SELECT * FROM outbox WHERE userId=%s AND sent=%s", (self.core.session.userId, 0))
		rowcount = dbiCursor.rowcount
		returnVal = rowcount
		while rowcount:
			message = dbiCursor.fetchone()
			pendingQueue.put(message)
			rowcount=rowcount-1
		
		self.core.dbi.done()
		return returnVal
		#send them?
	
	def processRetryQueue(self):
		while self.retryQueue.qsize()>0:	#They say some whack shit about this not being reliable in the documentation. Python -_-
			message = self.retryQueue.get()
			sendMessage(message)

	def sendMessage(self, message):
		#if self.core.isConnected == True:
		toJid = "%s@s.whatsapp.net" %message["recipient"]
		messageId = self.core.methodsInterface.call("message_send", (toJid, message["messageText"]))
		message["messageId"] = messageId
		message["tstamp"] = time.time() 
		self.logOutgoingMessage(message)

	def onMessageSent(self, jid, messageId):
		print "Message ack received for messageId: %s"%messageId
		updateMessageStatus(message, Constants.OUTBOX_SENT)
	
	def logOutgoingMessage(self,message):
		status = Constants.OUTBOX_SENDING
		timeNow = time.time()
		print "time is %d" %(timeNow)
		dbiCursor = self.core.dbi.getCursor()
		dbiCursor.execute("INSERT INTO outbox (sender,recipient,message,messageId,status,tstamp) VALUES(%s,%s,%s,%s,%s,%s)",( message["sender"], message["recipient"],message["messageText"], message["messageId"],status, timeNow) )
		self.core.dbi.commit()
		self.core.dbi.done()
	
	def updateMessageStatus(self,message, status):
		dbiCursor = self.queueDBI.getCursor()
		dbiCursor.execute("UPDATE outbox SET status=%s WHERE messageId=%s", ( status, message.messageId) )
		self.queueDBI.done()

	def resendTimedOut(self):
		#Reset the ones that have timedout so we can send them again... Assume they failed
		timeNow = time.time()
		treshold = timeNow - Config.OUTBOX_SENDTIMEOUT
		try:
			dbiCursor = self.queueDBI.getCursor()
			dbiCursor.execute("SELECT sender,recipient,message FROM outbox WHERE status=%s AND lastUpdated<%s", (OUTBOX_SENDING, treshold) )
			pending = dbiCursor.fetchall()
			for message in pending:
				self.pendingQueue.put(message)
			
			dbiCursor.execute("UPDATE outbox SET lastUpdated=%s WHERE status=%s AND lastUpdated<%s", (timeNow, OUTBOX_SENDING, treshold) )
		except MySQLdb.Error, e:
			print "resendTimedOut Exception: %s"%(e)
		finally:
			self.core.dbi.done()
	
