__file__ = 'Password_base64'
__date__ = '4/9/2015'
__author__ = 'ABREZNIC'
import base64

password = ""
encoded = base64.b64encode(password)
decoded = base64.b64decode(encoded)
print "Password: " + password
print "Encoded: " + encoded
print "Decoded: " + decoded

