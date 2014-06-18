import MySQLdb
from WWMException import WWMException
from Config import Config,Constants

import time
'''
Doing:
	Rewrite this to have a class DBICursor that has a deconstructor to call done. SO that we don't have an infinite block if we forget to call done
	How to do a query?
	with BlockingDBICursor(dbi_you_want_to_use) as dbiCursor:
		dbiCursor.execute() #and other stuff
		
'''

class DBI:	#Blocking DBI. ie, it blocks queries by not returning a cursor till it's free. Badly needs to be rewritten
	def __init__(self):
		self.dbi = None
		self.cursor = None
		self.connectedAt = 0
		self.connect()	#Hack
		self.waitTimeout = Config.DBI_getCursorTimeout
	
	def connect(self):
		try:
			#Check for existing connection
			if self.dbi!=None and self.dbi.open==1:
				self.dbi.close() #Just to make sure?
		
			print "RECONNECTING TO DB!"
			self.dbi = MySQLdb.connect(Config.mysql_host,Config.mysql_user,Config.mysql_password,Config.mysql_database)
			self.dbi.autocommit(True)
			self.cursor = self.dbi.cursor(MySQLdb.cursors.DictCursor)
			
			self.connectedAt = time.time()
			self.inUse =0
		except MySQLdb.Error, e:
			self.close()
			raise WWMException("MySQL could not connect: %s" %e)
	
	def getCursor(self):
		timeWaited = 0
		while self.inUse ==1 :
			if timeWaited>=self.waitTimeout:
				raise WWMException("The database connection is busy. Please try again in some time")
			time.sleep(1)
			timeWaited+=1
		
		self.inUse = 1
		return self.cursor
	
	def commit(self):
		print "Call to deprecated method DBI.commit"
		#self.dbi.commit()#deprecated since autocmmit
		
	def done(self):
		self.inUse = 0
	
	def close(self):
		#print "DBI.close WAS CALLED!"
		#Closing a connection to a connection crashes python
		if self.dbi!= None and self.dbi.open!=0:
			print "CLOSING CONN TO DB!"
			self.dbi.close()
		
		self.dbi = None
		self.dbiCursor = None
		self.connectedAt = 0
	


#With is perfect for this situation <3
class BlockingDBICursor:
	def __init__(self, parentDBIRef):
		self.parentDBI = parentDBIRef
	
	def __enter__(self):
		self.cursor = self.parentDBI.cursor
		return self.parentDBI.getCursor()
	
	def __exit__(self,type, value, tb):
		self.parentDBI.done()
	