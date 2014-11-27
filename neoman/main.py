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
import os
import sys
import argparse
import neoman.qt_resources
from PySide import QtGui, QtCore
from neoman.view.main import MainWindow
from neoman.model.neo import AvailableNeos
from neoman.model.applet import AppletManager
from neoman.worker import Worker
from neoman import __version__ as version, messages as m


if getattr(sys, 'frozen', False):
    # we are running in a PyInstaller bundle
    basedir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    basedir = os.path.dirname(__file__)

# Font fix for OSX
if sys.platform == 'darwin':
    from platform import mac_ver
    mac_version = tuple(mac_ver()[0].split('.'))
    if (10, 9) <= mac_version < (10, 10):  # Mavericks
        QtGui.QFont.insertSubstitution(".Lucida Grande UI", "Lucida Grande")
    if (10, 10) <= mac_version:  # Yosemite
        QtGui.QFont.insertSubstitution(".Helvetica Neue DeskInterface", "Helvetica Neue")


class NeomanApplication(QtGui.QApplication):

    def __init__(self, argv):
        super(NeomanApplication, self).__init__(argv)

        self._set_basedir()

        m._translate(self)

        QtCore.QCoreApplication.setOrganizationName(m.organization)
        QtCore.QCoreApplication.setOrganizationDomain(m.domain)
        QtCore.QCoreApplication.setApplicationName(m.app_name)

        args = self._parse_args()
        self.devmode = args.devmode

        self.available_neos = AvailableNeos()
        self.available_neos.start()
        self.aboutToQuit.connect(self.available_neos.stop)

        self.appletmanager = AppletManager()
        self.window = self._create_window()

        self.worker = Worker(self.window)
        self.aboutToQuit.connect(self.worker.work_thread.quit)
        self.appletmanager.update()

    def _parse_args(self):
        parser = argparse.ArgumentParser(description="YubiKey NEO Manager",
                                         add_help=True)
        parser.add_argument('-d', '--devmode', action='store_true',
                            default=False, help='enables features which '
                            'require the transport keys of the device to be '
                            'known')

        return parser.parse_args()

    def _set_basedir(self):
        if getattr(sys, 'frozen', False):
            # we are running in a PyInstaller bundle
            self.basedir = sys._MEIPASS
        else:
            # we are running in a normal Python environment
            self.basedir = os.path.dirname(__file__)

    def _create_window(self):
        window = MainWindow()
        window.setWindowTitle(m.win_title_1 % version)
        window.setWindowIcon(QtGui.QIcon(':/neoman.png'))
        window.show()
        window.raise_()
        return window


def main():
    app = NeomanApplication(sys.argv)
    status = app.exec_()
    app.deleteLater()
    sys.exit(status)
