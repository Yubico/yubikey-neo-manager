# Copyright (c) 2013 Yubico AB
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
from PySide import QtCore, QtWebKit
import os


class JS_API(QtCore.QObject):

    def __init__(self, neo, applet):
        super(JS_API, self).__init__()
        self._neo = neo
        self._applet = applet
        self._webpage = QtWebKit.QWebPage()
        self._frame = self._webpage.mainFrame()
        self._frame.addToJavaScriptWindowObject('_JS_API', self)

    def __enter__(self):
        basedir = QtCore.QCoreApplication.instance().basedir
        path = os.path.join(basedir, 'js_api.js')
        with open(path, 'r') as f:
            self._frame.evaluateJavaScript(f.read())
        return self

    def __exit__(self, type, value, traceback):
        del self._frame

    def run(self, script):
        return self._frame.evaluateJavaScript(script)

    @QtCore.Slot(str)
    def log(self, line):
        print "LOG [%s]: %s" % (self._applet.name, line)

    @QtCore.Slot(str, result=str)
    def send_apdu(self, apdu):
        return self._neo.send_apdu(apdu.decode('hex')).encode('hex')

    def _aid(self):
        return self._applet.aid

    aid = QtCore.Property(unicode, _aid)
