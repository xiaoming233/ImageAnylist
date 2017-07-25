# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 10:27:27 2017

@author: ljm
"""
import configparser
import sys

class ImagePath:
    filepath=''
    def __init__(self,path):
        self.conf = configparser.ConfigParser()
        self.conf.read(path)
        self.filepath=path
    def getPath(self):
        path=self.conf.get('path', 'value')
        return  path
    def setPath(self,impath):
        if impath!='':
            try:
                self.conf.set('path','value',impath)
                self.conf.write(open(self.filepath, 'w'))
            except:
                print("Unexpected error:", sys.exc_info()[0])
        
    
    