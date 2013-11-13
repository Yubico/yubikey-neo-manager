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
from PySide import QtGui
from PySide import QtCore
from neoman.model.neo import YubiKeyNeo
from neoman.model.applet import Applet
from neoman.view.nav import NavTree
from neoman.view.welcome import WelcomePage
from neoman.view.neo import NeoPage
from neoman.view.applet import AppletPage
from neoman.storage import settings


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setCentralWidget(self.build_ui())

        self.resize(settings.value('window/size', QtCore.QSize(0, 0)))
        pos = settings.value('window/pos')
        if pos:
            self.move(pos)

    def build_ui(self):
        widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.build_nav())
        layout.addWidget(self.build_main())

        self._nav.subpage.connect(self._main.setContent)
        self._main.setContent(self._nav.current)
        widget.setLayout(layout)

        return widget

    def build_nav(self):
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self._nav = NavTree()
        layout.addWidget(self._nav)

        widget = QtGui.QWidget()
        widget.setLayout(layout)

        widget.setMaximumWidth(200)
        widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                             QtGui.QSizePolicy.Expanding)
        return widget

    def build_main(self):
        self._main = ContentWidget()
        return self._main

    def closeEvent(self, event):
        settings.setValue('window/size', self.size())
        settings.setValue('window/pos', self.pos())
        event.accept()


class ContentWidget(QtGui.QStackedWidget):

    def __init__(self):
        super(ContentWidget, self).__init__()

        self._content = None

        self._start_page = WelcomePage()
        self.addWidget(self._start_page)

        self._neo_page = NeoPage()
        self.addWidget(self._neo_page)

        self._app_page = AppletPage()
        self.addWidget(self._app_page)

        self.setMinimumSize(420, 180)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

    @QtCore.Slot(object)
    def setContent(self, content):
        self._content = content

        if content is None:
            self._neo_page.setNeo(None)
            self.setCurrentWidget(self._start_page)
        elif isinstance(content, YubiKeyNeo):
            self._neo_page.setNeo(content)
            self.setCurrentWidget(self._neo_page)
        elif isinstance(content, Applet):
            self._app_page.setApplet(content)
            self.setCurrentWidget(self._app_page)
