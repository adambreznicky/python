__file__ = 'copytest'
__date__ = '8/18/2014'
__author__ = 'ABREZNIC'
import shutil, base64, smtplib
today = "2014_08_15"
workspace = "C:\\TxDOT\\Scripts\\QC\\Error Checks\\v12_2014_08_15"
try:
    tdrive = "T:\\DATAMGT\\MAPPING\\Data Quality Checks\\Errors_" + str(today)
    shutil.copytree(workspace, tdrive, ignore=shutil.ignore_patterns('*.gdb'))
    print "Copied to T Drive."

    FROM = 'adam.breznicky@txdot.gov'
    TO = ['adam.breznicky@txdot.gov']
    SUBJECT = "Error Checks for " + today
    TEXT = "TESTT"
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
                """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    username = "adam.breznicky@txdot.gov"
    password = base64.b64decode("U2F0dXJkYXkxMjM=")
    server = smtplib.SMTP('owa.txdot.gov', 25)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(FROM, TO, message)
    server.close()
    print "Email to yourself delivered."
except Exception, e:
    print "Failed to copy to the T-Drive and send emails."
    f = open(workspace + "\\error.txt", "w")
    issue = repr(e)
    f.write(issue)
    f.close()
    print issue