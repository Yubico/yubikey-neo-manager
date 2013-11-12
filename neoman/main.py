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
from PySide import QtGui, QtCore
from neoman.view.main import MainWindow
from neoman.model.neo import AvailableNeos
from neoman import __version__ as version


if getattr(sys, 'frozen', False):
    # we are running in a PyInstaller bundle
    basedir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    basedir = os.path.dirname(__file__)

# Font fix for OSX Mavericks
if sys.platform == 'darwin':
    from platform import mac_ver
    if tuple(mac_ver()[0].split('.')) >= (10, 9):
        QtGui.QFont.insertSubstitution(".Lucida Grande UI", "Lucida Grande")


QtCore.QCoreApplication.setOrganizationName('Yubico')
QtCore.QCoreApplication.setOrganizationDomain('yubico.com')
QtCore.QCoreApplication.setApplicationName('YubiKey NEO Manager')


def main():
    app = QtGui.QApplication(sys.argv)

    available_neos = AvailableNeos()
    available_neos.start()
    app.aboutToQuit.connect(available_neos.stop)
    app.available_neos = available_neos

    window = MainWindow()
    window.setWindowTitle("YubiKey NEO Manager (%s)" % version)
    window.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'neoman.png')))
    window.show()
    window.raise_()

    sys.exit(app.exec_())
