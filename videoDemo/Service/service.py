# -*- coding: utf-8 -*-
"""
Created on Web Augus 9 15:10:32 2017

@author: ljm
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import os
class PostHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     }
        )
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes('Client: %sn ' % str(self.client_address), 'utf8'))
        self.wfile.write(bytes('User-agent: %sn' % str(self.headers['user-agent']), 'utf8'))
        self.wfile.write(bytes('Path: %sn' % self.path, 'utf8'))
        self.wfile.write(bytes('Form data:n', 'utf8'))
        for field in form.keys():
            field_item = form[field]
            filename = field_item.filename
            filevalue = field_item.value
            path = os.path.join(os.path.abspath('./Images'), filename)
            with open(path, 'wb') as f:
                f.write(filevalue)
        return
if __name__=='__main__':
    sever = HTTPServer(('localhost',8088),PostHandler)
    print ('Starting server, use <Ctrl-C> to stop')
    sever.serve_forever()
