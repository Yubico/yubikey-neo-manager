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
from neoman.model.applet import Applet


class AppletPage(QtGui.QTabWidget):
    applet = QtCore.Signal(Applet)

    def __init__(self):
        super(AppletPage, self).__init__()
        self._applet = None

        overview = OverviewTab()
        self.applet.connect(overview.set_applet)
        self.addTab(overview, "Overview")

    def setApplet(self, applet):
        self._applet = applet
        self.applet.emit(applet)


class OverviewTab(QtGui.QWidget):

    def __init__(self):
        super(OverviewTab, self).__init__()
        self._applet = None
        self._name = QtGui.QLabel()
        self._aid = QtGui.QLabel()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._name)
        layout.addWidget(self._aid)
        layout.addStretch()

        self.setLayout(layout)

    @QtCore.Slot(Applet)
    def set_applet(self, applet):
        self._applet = applet
        self._name.setText("Name: %s" % applet.name)
        self._aid.setText("AID: %s" % applet.aid)
