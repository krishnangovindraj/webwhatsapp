#CDBITest
from CallbackDBI import CallbackDBI

db = CallbackDBI()
queryStr = "INSERT INTO numwums (num,numsquare,numcube) VALUES(%s,%s,%s)"
for i in range(2,10):
	args = (i, i*i,i*i*i)
	db.addToQueue((queryStr, args))


db.execute(queryStr, (0,0,0))
'''
while db.queryQueue.qsize()>0:
	q =db.queryQueue.get()
	print q
	print "\n"
'''