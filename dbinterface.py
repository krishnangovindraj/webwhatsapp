import MySQLdb
from WWMException import WWMException

import time

class DBI:
	def __init__(self):
		self.dbi = None
		self.cursor = None
		self.connectedAt = 0
		self.connect()	#Hack
	
	def connect(self):
		try:
			print "RECONNECTING TO DB!"
			self.dbi = MySQLdb.connect('localhost','root','','webwhatsapp')
			self.cursor = self.dbi.cursor(MySQLdb.cursors.DictCursor)
			self.connectedAt = time.time()
			self.userThreads =0
		except MySQLdb.Error, e:
			self.close()
			raise WWMException("MySQL could not connect: %s" %e)
	
	def getCursor(self):
		#if self.dbi == None or self.dbi.open==0:
		#	self.connect()
		
		self.userThreads = self.userThreads+1
		return self.cursor
	
	def commit(self):
		self.dbi.commit()
		
	def done(self):
		self.userThreads= self.userThreads-1
		#if self.userThreads <= 0:
		#	self.close()
	
	def close(self):
		
		#Closing a connection to a connection crashes python
		if self.dbi!= None and self.dbi.open!=0:
			print "CLOSING CONN TO DB!"
			#self.dbi.commit()
			self.dbi.close()
		#self.dbi = None
		self.dbiCursor = None
		self.connectedAt = 0
