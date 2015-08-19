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
import sys
import time
import argparse
import signal
import neoman.qt_resources
from PySide import QtGui, QtCore

from neoman.view.main import CentralWidget
from neoman.model.neo import AvailableNeos
from neoman.model.applet import AppletManager
from neoman import __version__ as version, messages as m
from neoman.yubicommon import qt


class NeomanApplication(qt.Application):

    def __init__(self, argv):
        super(NeomanApplication, self).__init__(m)

        QtCore.QCoreApplication.setOrganizationName(m.organization)
        QtCore.QCoreApplication.setOrganizationDomain(m.domain)
        QtCore.QCoreApplication.setApplicationName(m.app_name)

        args = self._parse_args()
        self.devmode = args.devmode

        self.available_neos = AvailableNeos()
        self.available_neos.start()
        self.aboutToQuit.connect(self.available_neos.stop)

        self.appletmanager = AppletManager()
        self._init_window()

        self.appletmanager.update()

    def _parse_args(self):
        parser = argparse.ArgumentParser(description="YubiKey NEO Manager",
                                         add_help=True)
        parser.add_argument('-d', '--devmode', action='store_true',
                            default=False, help='enables features which '
                            'require the transport keys of the device to be '
                            'known')

        return parser.parse_args()

    def _init_window(self):
        self.window.setWindowTitle(m.win_title_1 % version)
        self.window.setWindowIcon(QtGui.QIcon(':/neoman.png'))
        self.window.setCentralWidget(CentralWidget())
        self.window.show()
        self.window.raise_()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = NeomanApplication(sys.argv)
    status = app.exec_()
    app.worker.thread().quit()
    app.deleteLater()
    time.sleep(0.01)
    sys.exit(status)


if __name__ == '__main__':
    main()