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
from PySide import QtCore

__all__ = [
    'CONFIG_HOME',
    'settings',
    'capstore'
]

CONFIG_HOME = os.path.join(os.path.expanduser('~'), '.neoman')

settings = QtCore.QSettings(os.path.join(CONFIG_HOME, 'settings.ini'),
                            QtCore.QSettings.IniFormat)


class AppletCapStore(object):

    def __init__(self, basedir):
        self._dir = basedir

    def _build_fname(self, aid, version):
        return os.path.join(self._dir, aid, '%s.cap' % version)

    def has_file(self, aid, version):
        return os.path.isfile(self._build_fname(aid, version))

    def get_filename(self, aid, version):
        fname = self._build_fname(aid, version)
        if not self.has_file(aid, version):
            raise ValueError("File not found: %s" % fname)
        return fname

    def store_data(self, aid, version, data):
        fname = self._build_fname(aid, version)
        QtCore.QDir.root().mkpath(os.path.dirname(fname))
        target = QtCore.QFile(fname)
        target.open(QtCore.QIODevice.WriteOnly)
        if target.write(data) == -1:
            raise ValueError("Unable to write data!")
        target.close()


capstore = AppletCapStore(os.path.join(CONFIG_HOME, 'applets'))
