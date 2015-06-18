__file__ = 'email_test'
__date__ = '8/1/2014'
__author__ = 'ABREZNIC'
import smtplib, base64
#
# FROM = 'adam.breznicky@txdot.gov'
# TO = ['tom.neville@txdot.gov'] #must be a list
# SUBJECT = "Testing sending using python"
# TEXT = "tom, holler at me if you received this email"
# message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
#             """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
# username = "adam.breznicky@txdot.gov"
# password = base64.b64decode("U2F0dXJkYXkxMjM=")
# server = smtplib.SMTP('owa.txdot.gov', 25)
# server.ehlo()
# server.starttls()
# server.ehlo()
# server.login(username, password)
# server.sendmail(FROM, TO, message)
# server.close()
# print base64.b64encode("Sunday123")
print base64.b64decode("U3VuZGF5MTIz")