import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

class Mailer(object):
    """docstring for Mailer."""
    def __init__(self):
        super(Mailer, self).__init__()
        apiPath = 'API.txt'
        with open(apiPath) as f:
            l_strip = [s.strip() for s in f.readlines()]
            self.ADDRESS    = l_strip[2]
            self.PASSWORD   = l_strip[3]
        return

    def message(self, to_address, subject, body):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From']    = self.ADDRESS
        msg['To']      = to_address
        msg['Date']    = formatdate()
        return msg

    def send(self, to_address, subject, msg):
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(self.ADDRESS, self.PASSWORD)
        smtpObj.sendmail(self.ADDRESS, to_address, self.message(to_address, subject, msg).as_string())
        smtpObj.close()

if __name__ == '__main__':
    mail = Mailer()
    subject = "Important message!!!"
    body = "Test Message from Python"
    to_address = "kuzumaki-issei-sk@ynu.jp"
    mail.send(to_address, subject, body)
    print('Test message has sent.')
    pass
