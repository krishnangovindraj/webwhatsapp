import MySQLdb
from WWMException import WWMException
from Config import Config,Constants

import time, Queue

class CallbackDBI:
	def __init__(self):
		self.dbi = None
		self.cursor = None
		self.connectedAt = 0
		self.connect()	#Hack
		self.waitTimeout = Config.CallbackDBI_queryTimeout
		self.queryQueue = Queue.Queue(50)
	
	def connect(self):
		try:
			print "CallbackDBI CONNECTING TO DB!"
			self.dbi = MySQLdb.connect(Config.mysql_host,Config.mysql_user,Config.mysql_password,Config.mysql_database)
			self.cursor = self.dbi.cursor(MySQLdb.cursors.DictCursor)
			#All hail autocommit!
			self.dbi.autocommit(True)
			
			self.connectedAt = time.time()
			self.inUse =0
			
		except MySQLdb.Error, e:
			self.close()
			raise WWMException("MySQL could not connect: %s" %e)
	
	def addToQueue(self, queryTup):
		self.queryQueue.put(queryTup)
	
	def processQueue(self):
		while self.queryQueue.qsize()>0:
			q = self.queryQueue.get()
			queryStr, args = q
			self.executeQuery(queryStr,args)
	
	def execute(self,queryStr, args):
		waitingFor = 0
		while self.inUse:
			if waitingFor>=self.waitTimeout:
				self.addToQueue((queryStr,args))	#the 
				return
			
			time.sleep(1)
			waitingFor+= 1
			
		self.inUse = 1
		self.executeQuery(queryStr,args)
		self.processQueue()	#Whichever query was added 
		
		self.inUse = 0
	
	def executeQuery(self,queryStr,args): #Yes, It needs to be this complicated.
		self.cursor.execute(queryStr,args)
	
	
	def close(self):
		print "DBI.close WAS CALLED!"
		#Closing/Querying a closed connection crashes python. So be careful
		if self.dbi!= None and self.dbi.open!=0:
			print "CLOSING CONN TO DB!"
			self.dbi.close()
		self.dbi = None
		self.dbiCursor = None
		self.connectedAt = 0
