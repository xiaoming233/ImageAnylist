# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 09:10:59 2017

@author: ljm
"""

import urllib
response=urllib.request.urlopen('http://www.baidu.com/')  
#response = urllib3.urlopen('http://www.baidu.com/')  
html = response.read()
html=html.decode('utf-8')  
print (html)