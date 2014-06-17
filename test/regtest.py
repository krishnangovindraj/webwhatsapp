import re
jid = "919975199490@s.whatsapp.net"
print re.match('([0-9]*)@s\.whatsapp\.net',jid).group(1)