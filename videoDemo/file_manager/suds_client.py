#!/usr/bin/env python

from suds.client import Client
import base64

# Suds does not support base64binary type, so we do the encoding manually.

# file = open('1.jpg', 'rb')
# file_data = base64.b64encode(file.read())
#
# print(type(file_data))
#file_data = base64.b64encode(file_data)

c=Client('http://localhost:9000/filemgr/?wsdl')
return_data=c.service.get('1.jpg')
# c.service.add('1.jpg', file_data)
f = open('132.jpg', 'wb')
file = base64.b64decode(return_data)
f.write(file)
f.close()
print(type(return_data))
print(repr(return_data))
print('file written.')

file_data = base64.b64encode('file_data')

c=Client('http://localhost:9000/filemgr/?wsdl')
c.service.add('x', 'y', 'file_name', file_data)

print('file written.')
print()

print('incoming data:')
return_data = c.service.get('file_name')
print(repr(return_data))