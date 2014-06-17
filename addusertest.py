#addUserTest
from Core import WWMCore

core = WWMCore()
db = core.getDBICursor()
db.execute("SELECT * FROM users WHERE 1")
core.initDBI()
#print db.fetchone()

phone ='' #country code followed by 10 digit
name = ''
password = ''
email = ''
whatsapp_pass=''
core.addUser(phone,email, name,password,whatsapp_pass)