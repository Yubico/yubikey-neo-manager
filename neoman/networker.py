# Copyright (c) 2015 Yubico AB
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

from PySide import QtCore, QtNetwork
from time import sleep


class NetWorker:

    def __init__(self, worker):
        self._done = None
        self._dl = None
        self._worker = worker
        self._manager = QtNetwork.QNetworkAccessManager()
        self._manager.finished.connect(self._dl_done)

    def download(self, url, callback=None):
        self._done = False

        def mark_done(result):
            self._done = True
            callback(result)

        def dl():
            self.download_bg(url, mark_done)
            while not self._done:
                sleep(0.1)
        self._worker.post('Downloading...', dl)

    def download_bg(self, url, callback=None):
        url = QtCore.QUrl(url)
        request = QtNetwork.QNetworkRequest(url)
        response = self._manager.get(request)
        self._dl = (request, response, callback)

    def _dl_done(self):
        (req, resp, callback) = self._dl
        del self._dl
        if callback:
            result = resp.error()
            if result is QtNetwork.QNetworkReply.NoError:
                result = resp.readAll()
            resp.close()
            callback(result)