# -*- coding: 'utf-8' -*-
from datetime import datetime
import emailMessanger as email

def sendError(contents):
    mail = email.Mailer()
    subject = "BitTrader Error Info!!"
    body = contents
    to_address = "kuzumaki-issei-sk@ynu.jp"
    mail.send(to_address, subject, body)

def getTimestamp():
    now = datetime.now()
    unix = int(now.timestamp())
    return str(unix)

def output(e):
    path = './error_log/' + getTimestamp() + '.log'
    with open(path, mode='w') as f:
        f.write(e)
    # sendError(e)
    return
