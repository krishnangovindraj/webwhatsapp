import MySQLdb, wwmException

class DBInterface:
	def __init__(self,coreRef):
		self.core = coreRef
		self.con = null
		self.cursor = null

	def connect(self):
		try:
			self.con = MySQLdb.connect('localhost','root','','webwhatsapp');
			self.cursor = self.con.cursor()
				
		except myDB.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])
			sys.exit(1)

	def storeMessage(self, sender, message, tstamp)
		self.cursor.execute("INSERT INTO inbox (recipientId, sender, message, tstamp, seen ) VALUES( %s, %s, %s, %s, %s )", 
			( self.session.userId, sender, message, tstamp, ,0))

	def getAuthData(self, userId):
		self.cursor.execute("SELECT phone, whatsapp_pass FROM users WHERE userId=%s ", (userId))
		if cursor.rowcount:
			return cursor.fetchone()
		else
			raise wwmException('Invalid userId')
	
	
	# disconnect from server
	def close():
		if self.dbh:
			self.dbh.close()