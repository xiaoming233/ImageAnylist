#!/usr/bin/env python
# encoding: utf8
#
# Copyright © Burak Arslan <burak at arskom dot com dot tr>,
#             Arskom Ltd. http://www.arskom.com.tr
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    3. Neither the name of the owner nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


"""As the Xml Schema standard does not define a file primitive, the File type
in the HTTP example does not work with Soap11 protocol. This is how you should
handle binary data with Soap in Spyne.

There is MTOM code inside Spyne but it lacks tests so it is not working as of
now.
"""


import logging
logger = logging.getLogger(__name__)
import os

from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.exceptions import NotFound
from werkzeug.serving import run_simple

from spyne.application import Application
from spyne.decorator import rpc
from spyne.service import ServiceBase
from spyne.error import ResourceNotFoundError
from spyne.error import ValidationError
from spyne.model.binary import File
from spyne.model.binary import ByteArray
from spyne.model.primitive import Unicode
from spyne.model.primitive import Mandatory
from spyne.server.wsgi import WsgiApplication
from spyne.protocol.soap import Soap11
from wsgiref.simple_server import make_server
import base64
import cv2
import numpy as np
from PIL import Image
import io

BLOCK_SIZE = 8192
port = 9000
ip = '127.0.0.1'

class FileServices(ServiceBase):
    @rpc(Mandatory.Unicode, _returns=ByteArray(encoding='hex'))
    def get(self, file_name):
        path = os.path.join(os.path.abspath('./files'), file_name)
        print(path)
        if not path.startswith(os.path.abspath('./files')):
            raise ValidationError(file_name)

        try:
            f = open(path, 'rb')
        except IOError:
            raise ResourceNotFoundError(file_name)

        self.transport.resp_headers['Content-Disposition'] = (
                                         'attachment; filename=%s;' % file_name)

        data = f.read(BLOCK_SIZE)
        while len(data) > 0:
            yield data
            data = f.read(BLOCK_SIZE)

        f.close()

    @rpc(Unicode, ByteArray)
    def add(self, file_name, file_data):
        path = os.path.join(os.path.abspath('./files'), file_name)
        if not path.startswith(os.path.abspath('./files')):
            raise ValidationError(file_name)

        f = open(path, 'wb') # if this fails, the client will see an
                            # internal error.

        # im=np.ndarray
        # im_data = b''
        # im_bytes = bytearray()
        logger.info("file_datalen: %r" % len(file_data))
        for data in file_data:
            pass
            # im_bytes.append(base64.urlsafe_b64decode(data))

        im_data = base64.urlsafe_b64decode(file_data[0])
        logger.info("im_data: %r" % len(im_data))
        f.write(im_data)
        # im = Image.open(io.BytesIO(im_data))
        # im.save(path)
        # arr_np = np.fromstring(im_bytes)
        # im = cv2.imdecode(arr_np, cv2.CV_LOAD_IMAGE_COLOR)
        # cv2.imwrite(path, im)
        # logger.info("im: %r" % type(im))
        # for data in file_data:
        #     im=base64.b64decode(data)
        #     logger.info("im: %r" % type(im))

        # cv2.imwrite(path, file)
        logger.debug("File written: %r" % file_name)
        f.close()
        try:
            # file = base64.urlsafe_b64decode(file_data)
            # # f.write(file)
            # # for data in file_data:
            # #     file = base64.b64decode(data)
            # #     f.write(file)
            # logger.info("FilePath written: %r" % path)
            # cv2.imwrite(path, file)
            # logger.debug("File written: %r" % file_name)

            # f.close()
            pass
        except:
            # f.close()
            os.remove(file_name)
            logger.debug("File removed: %r" % file_name)
            raise type(file_data)# again, the client will see an internal error.

    @rpc(File.customize(min_occurs=1, nullable=False))
    def add_file(self,  file):
        # logger.info("Person Type: %r" % person_type)
        # logger.info("Action: %r" % action)

        path = os.path.join(os.path.abspath('./files'), file.name)
        if not path.startswith(os.path.abspath('./files')):
            raise ValidationError(file.name)

        f = open(path, 'w') # if this fails, the client will see an
                            # internal error.

        try:
            for data in file.data:
                f.write(data)

            logger.debug("File written: %r" % file.name)

            f.close()

        except:
            f.close()
            os.remove(file.name)
            logger.debug("File removed: %r" % file.name)
            raise # again, the client will see an internal error.
def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
    filemgr_app = WsgiApplication(Application([FileServices],
            tns='spyne.examples.file_manager',
            in_protocol=Soap11(validator='lxml'),
            out_protocol=Soap11()
        ))

    try:
        os.makedirs('./files')
    except OSError:
        pass

    wsgi_app = DispatcherMiddleware(NotFound(), {'/filemgr': filemgr_app})

    return run_simple('localhost', port, wsgi_app, static_files={'/': 'static'},threaded=True)
    # server = make_server(ip, port, filemgr_app)
    # server.serve_forever()

if __name__ == '__main__':
    import sys
    sys.exit(main())
    # # logging.basicConfig(level=logging.DEBUG)
    # # logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
    # filemgr_app = WsgiApplication(Application([FileServices],
    #         tns='spyne.examples.file_manager',
    #         in_protocol=Soap11(validator='lxml'),
    #         out_protocol=Soap11()
    #     ))
    #
    # try:
    #     os.makedirs('./files')
    # except OSError:
    #     pass
    #
    # #wsgi_app = DispatcherMiddleware(NotFound(), {'/filemgr': filemgr_app})
    #
    # #return run_simple('localhost', port, wsgi_app, static_files={'/': 'static'},threaded=True)
    # server = make_server(ip, port, filemgr_app)
    # server.serve_forever()
