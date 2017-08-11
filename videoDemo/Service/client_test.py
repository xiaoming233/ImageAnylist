# -*- coding: utf-8 -*-
"""
Created on Web Augus 9 16:56:14 2017

@author: ljm
"""
import requests
url = 'http://localhost:8088'
path = u'test2.jpg'
print(path)
files = {'file': open(path, 'rb')}
r = requests.post(url, files=files)
print(r.content)