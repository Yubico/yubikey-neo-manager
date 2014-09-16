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
from neoman import __version__ as version, messages as m
from neoman.device_ccid import libversion as ykneomgr_version
from neoman.device_otp import libversion as ykpers_version
from neoman.device_u2f import libversion as u2fh_version
import os


FORUM_URL = "http://yubi.co/forum"
ABOUT_TEXT = """
<h2>%s</h2>
%s<br>
%s
<h4>%s</h4>
%s
<br><br>
%s
""" % (m.app_name, m.copyright, m.version_1, m.libraries, '%s',
       m.about_link_1 % FORUM_URL)


class TabWidgetWithAbout(QtGui.QTabWidget):
    def __init__(self):
        super(TabWidgetWithAbout, self).__init__()

        btn = QtGui.QToolButton()

        basedir = QtCore.QCoreApplication.instance().basedir
        icon = QtGui.QIcon(os.path.join(basedir, 'icon-about.png'))
        btn.setIcon(icon)
        btn.clicked.connect(self._about)

        self.setCornerWidget(btn)

    def _libversions(self):
        libs = []
        libs.append('libykneomgr: %s' % ykneomgr_version)
        libs.append('ykpers: %s' % ykpers_version)
        libs.append('libu2f-host: %s' % u2fh_version)
        return '<br>'.join(libs)

    def _about(self):
        QtGui.QMessageBox.about(
            self,
            m.about_1 % m.app_name,
            ABOUT_TEXT % (version, self._libversions())
        )
