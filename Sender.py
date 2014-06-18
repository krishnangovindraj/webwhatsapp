'''
	Sender
'''

import Queue, time, datetime
from Config import Config,Constants
from DBInterface import DBI, BlockingDBICursor
class Sender:
	def __init__(self,coreRef):
		print "initing Sender"
		self.core = coreRef
		#if Config.waitForReceipts:
		
		self.core.signalsInterface.registerListener("receipt_messageSent", self.onMessageSent)
		
		self.lastReadPending = 0	#To make sure we don't read pending messages twice
		self.retryQueue= Queue.Queue()	#50 messages is pushing it
		self.priority = Queue.Queue()	#50 messages is pushing it
		self.queueDBI = DBI() #Needs to be a blocking DBI
		
		self.lastResend = time.time()

	def getPendingMessages(self):
		resetTimedout()
		with BlockingDBICursor(self.core.dbi) as dbiCursor:
			dbiCursor.execute("SELECT * FROM outbox WHERE userId=%s AND sent=%s", (self.core.session.userId, 0))
			rowcount = dbiCursor.rowcount
			returnVal = rowcount
			while rowcount:
				message = dbiCursor.fetchone()
				retryQueue.put(message)
				rowcount=rowcount-1
			
		return returnVal
		#send them?
	

	def sendMessage(self, message):
		#if self.core.isConnected == True:
		toJid = "%s@s.whatsapp.net" %message["recipient"]
		messageId = self.core.methodsInterface.call("message_send", (toJid, message["messageText"]))
		message["messageId"] = messageId
		message["tstamp"] = time.time() 
		self.logOutgoingMessage(message)

	def onMessageSent(self, jid, messageId):
		print "Message ack received for messageId: %s"%messageId
		self.updateMessageStatus(messageId, Constants.OUTBOX_SENT)
		#What a good time to resend failed messages
		timeNow = time.time()
		if (timeNow-self.lastResend)>Config.Sender_resendInterval:
			self.resendTimedOut()
	
	def logOutgoingMessage(self,message):
		status = Constants.OUTBOX_SENDING
		timeNow = time.time()
		print "time is %d" %(timeNow)
		
		isRetry = message.get("isRetry",None)
		if isRetry!=None and isRetry== True:
			with BlockingDBICursor(self.core.dbi) as dbiCursor:
				dbiCursor.execute("UPDATE outbox SET status=%s, lastupdated=%s, messageId=%s WHERE messageId=%s",( Constants.OUTBOX_SENDING, timeNow, message["messageId"],message["originalMessageId"]) )
		else:			
			with BlockingDBICursor(self.core.dbi) as dbiCursor:
				dbiCursor.execute("INSERT INTO outbox (sender,recipient,message,messageId,status,tstamp,lastupdated) VALUES(%s,%s,%s,%s,%s,%s,%s)",( message["sender"], message["recipient"],message["messageText"], message["messageId"],status, timeNow, timeNow) )
		
	
	def updateMessageStatus(self,messageId, status):
		with BlockingDBICursor(self.queueDBI) as dbiCursor:
			dbiCursor.execute("UPDATE outbox SET status=%s WHERE messageId=%s", ( status, messageId) )
		

	def resendTimedOut(self):
		self.lastResend = time.time()
		#Reset the ones that have timedout so we can send them again... Assume they failed
		timeNow = time.time()
		treshold = timeNow - Config.outbox_retryInterval
		try:
			with BlockingDBICursor(self.queueDBI) as dbiCursor:
				dbiCursor.execute("SELECT messageId, sender,recipient,message as messageText,tstamp FROM outbox WHERE status=%s AND lastupdated<%s", (Constants.OUTBOX_SENDING, treshold) )
				pending = dbiCursor.fetchall()
				for message in pending:
					self.retryQueue.put(message)
				
				dbiCursor.execute("UPDATE outbox SET lastupdated=%s WHERE status=%s AND lastupdated<%s", (timeNow, Constants.OUTBOX_SENDING, treshold) )
			
		except Exception, e:
			print "resendTimedOut Exception: %s"%(e)
		
		self.processRetryQueue()
		
	
	
	def processRetryQueue(self):
		while self.retryQueue.qsize()>0:	#They say some whack shit about this not being reliable in the documentation. Python -_-
			message = self.retryQueue.get()
			originalTime = datetime.datetime.fromtimestamp(int(message["tstamp"])).strftime('%d/%m/%Y | %H:%M:%S')
			resendnote = "[Resend after failure: Originally sent @ %s]\n"%(originalTime)
			message["messageText"] =  resendnote + message["messageText"] 
			message["isRetry"] = True
			message["originalMessageId"] = message["messageId"] # To update the table instead of inserting new row
			self.sendMessage(message)
			print "RETRY QUEUE SEND++"
		print "Completed retry queue process."
	
