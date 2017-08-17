# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 09:10:59 2017

@author: ljm
"""

from suds.client import Client
import base64
import cv2
import io
from PIL import Image
print('-' * 10)
with open('test.JPG', 'rb') as file:
    file_data = base64.b64encode(file.read())
    print(type(file_data))
    client = Client('http://localhost:9000/filemgr/?wsdl')
    #client.service.add('13.jpg', file_data)
# img=Image.open('1.jpg')
# img_bytes=io.BytesIO()
# img.save(img_bytes,format='png')
# print(len(img_bytes.getvalue()))
# file_data = base64.urlsafe_b64encode(img_bytes.getvalue())
# print(len(file_data))
# client = Client('http://localhost:9000/filemgr/?wsdl')
# print (client)
#client.service.add_file(base64.urlsafe_b64encode(open('1.jPG', 'rb').read()))
