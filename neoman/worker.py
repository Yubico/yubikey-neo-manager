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
from PySide import QtGui, QtCore


class Worker(QtCore.QObject):
    work_signal = QtCore.Signal(tuple)
    work_done = QtCore.Signal(object)
    work_done_0 = QtCore.Signal()

    def __init__(self):
        super(Worker, self).__init__()

        self.work_signal.connect(self.work)

        self.busy = QtGui.QProgressDialog('', None, 0, 0)
        self.busy.setWindowModality(QtCore.Qt.WindowModal)
        self.busy.setMinimumDuration(0)
        self.busy.setAutoClose(True)
        self.work_done_0.connect(self.busy.reset)

        self.work_thread = QtCore.QThread()
        self.moveToThread(self.work_thread)
        self.work_thread.start()

    def post(self, title, fn, callback=None):
        self.busy.setLabelText(title)
        self.busy.show()
        self.work_signal.emit((fn, callback))

    @QtCore.Slot(tuple)
    def work(self, job):
        QtCore.QThread.msleep(10)  # Needed to yield
        (fn, callback) = job
        try:
            result = fn()
        except Exception as e:
            result = e
        if callback:
            self.work_done.connect(callback)
            self.work_done.emit(result)
            self.work_done.disconnect(callback)
            self.work_done_0.emit()
