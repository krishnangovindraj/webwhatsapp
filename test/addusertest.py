#addUserTest
from Core import WWMCore

core = WWMCore()
core.initDBI()

phone ='919975199490' #country code followed by 10 digit
name = 'Krishnan Govindraj'
password = 'weakpass'
email = 'f2012207@goa.bits-pilani.ac.in'
whatsapp_pass='GwpsEyeo4PwqMT8hRXY2tpQnb88='
#AESKey = core.genAESKey(password)
core.addUser(phone,email, name,password,whatsapp_pass)
