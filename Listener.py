'''
Copyright (c) <2012> Tarek Galal <tare2.galal@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import datetime, sys, re

from Yowsup.connectionmanager import YowsupConnectionManager
from Config import Config,Constants
from DBInterface import DBI
import MySQLdb
class Listener:
	
	def __init__(self, coreRef):
		print "initing Sender"
		self.core = coreRef
		self.core.signalsInterface.registerListener("message_received", self.onMessageReceived)	
		#self.listenerDBI = DBI()
	
	def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt, pushName, isBroadCast):
		print "received message: %s,%s, %s"%(messageId, jid, messageContent)
		sender = re.match('([0-9]*)@s\.whatsapp\.net',jid).group(1)
		
		try:
			dbiCursor = self.core.dbi.getCursor()#self.listenerDBI.getCursor()
			#self.core.dbiCursor.execute("INSERT INTO inbox (messageId, recipient, sender, message, tstamp, seen ) VALUES( %s, %s, %s, %s, %s, %s )", ( messageId, self.core.session.phone, sender, messageContent, timestamp, 0))
			dbiCursor.execute("REPLACE INTO inbox (messageId, recipient, sender, message, tstamp, seen ) VALUES( %s, %s, %s, %s, %s, %s )", ( messageId, self.core.session.phone, sender, messageContent, timestamp, 0))
			self.core.dbi.commit()#self.listenerDBI.commit()
		except MySQLdb.Error, e:
			print "Exception onMessageReceived: %s"%e
		finally:
			self.core.dbi.done()#self.listenerDBI.done()
		
		if wantsReceipt and Config.sendReceipts:
			self.methodsInterface.call("message_ack", (jid, messageId))
	
