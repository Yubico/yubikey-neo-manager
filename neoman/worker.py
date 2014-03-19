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
from PySide import QtGui, QtCore, QtNetwork
from functools import partial
from neoman import messages as m


class _Event(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, callback):
        super(_Event, self).__init__(_Event.EVENT_TYPE)
        self.callback = callback


class QtWorker(QtCore.QObject):
    _work_signal = QtCore.Signal(tuple)
    _work_done = QtCore.Signal(object)
    _work_done_0 = QtCore.Signal()

    def __init__(self, window):
        super(QtWorker, self).__init__()

        self.window = window

        self.busy = QtGui.QProgressDialog('', None, 0, 0, window)
        self.busy.setWindowTitle(m.wait)
        self.busy.setWindowModality(QtCore.Qt.WindowModal)
        self.busy.setMinimumDuration(0)
        self.busy.setAutoClose(True)

        self.work_thread = QtCore.QThread()
        self.moveToThread(self.work_thread)
        self.work_thread.start()

        self._work_signal.connect(self.work)
        self._work_done_0.connect(self.busy.reset)

        self._manager = QtNetwork.QNetworkAccessManager()
        self._manager.finished.connect(self._work_done_0)
        self._manager.finished.connect(self._dl_done)

    def post(self, title, fn, callback=None):
        self.busy.setLabelText(title)
        self.busy.show()
        self.post_bg(fn, callback)

    def post_bg(self, fn, callback=None):
        self._work_signal.emit((fn, callback))

    def download(self, url, callback=None):
        self.busy.setLabelText(m.downloading_file)
        self.busy.show()
        self.download_bg(url, callback)

    def download_bg(self, url, callback=None):
        url = QtCore.QUrl(url)
        request = QtNetwork.QNetworkRequest(url)
        response = self._manager.get(request)
        self._dl = (request, response, callback)

    def _dl_error(self):
        (req, resp, callback) = self._dl
        del self._dl
        if callback:
            event = _Event(partial(callback, resp.error()))
            QtGui.QApplication.postEvent(self.window, event)

    def _dl_done(self):
        (req, resp, callback) = self._dl
        del self._dl
        if callback:
            result = resp.error()
            if result is QtNetwork.QNetworkReply.NoError:
                result = resp.readAll()
            resp.close()
            event = _Event(partial(callback, result))
            QtGui.QApplication.postEvent(self.window, event)

    @QtCore.Slot(tuple)
    def work(self, job):
        QtCore.QThread.msleep(10)  # Needed to yield
        (fn, callback) = job
        try:
            result = fn()
        except Exception as e:
            result = e
        if callback:
            event = _Event(partial(callback, result))
            QtGui.QApplication.postEvent(self.window, event)
        self._work_done_0.emit()

Worker = QtWorker
