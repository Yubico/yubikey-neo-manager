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
from PySide import QtCore, QtGui
from neoman.device import open_first_device
from neoman.storage import settings


class YubiKeyNeo(QtCore.QObject):

    def __init__(self, device):
        super(YubiKeyNeo, self).__init__()

        self._mutex = QtCore.QMutex()

        self._dev = device
        self._mode = device.mode
        self._serial = device.serial
        self._version = device.version

        self._group = self._serial if self._serial else "NOSERIAL"

    def _set_device(self, device):
        assert self.serial == device.serial
        assert self.version == device.version
        self._dev = device
        self._mode = device.mode

    def __setitem__(self, key, value):
        settings.setValue('%s/%s' % (self._group, key), value)

    def __getitem__(self, key):
        return self.get(key)

    def __getattr__(self, name):
        try:
            self._mutex.lock()
            if not self._dev:
                raise AttributeError(name)
            return getattr(self._dev, name)
        finally:
            self._mutex.unlock()

    def get(self, key, default=None):
        return settings.value('%s/%s' % (self._group, key), default)

    @property
    def name(self):
        return self.get('name', 'YubiKey NEO')

    @name.setter
    def name(self, new_name):
        self['name'] = new_name

    @property
    def mode(self):
        return self._mode

    @property
    def serial(self):
        return self._serial

    @property
    def version(self):
        return self._version

    def __str__(self):
        return "%s[%d]" % (self.name, self.mode)


class AvailableNeos(QtCore.QThread):
    changed = QtCore.Signal(list)

    def __init__(self):
        super(AvailableNeos, self).__init__()

        self._neos = []
        self._running = True

    def stop(self):
        self._running = False
        self.wait()

    def run(self):
        while self._running:
            if QtGui.QApplication.activeWindow():  # Only if we have focus
                self.discover_devices()
            self.msleep(1000)

    def discover_devices(self):
        neos = self._neos[:]
        for neo in neos:
            if neo._dev:
                neo._mutex.lock()
                neo._dev = None

        single = open_first_device()
        discovered = [single] if single else []

        new_neos = []
        for dev in discovered:
            for neo in neos:
                if dev.serial == neo.serial:
                    neo._set_device(dev)
                    neo._mutex.unlock()
                    break
            else:
                new_neos.append(YubiKeyNeo(dev))

        dead_neos = [x for x in neos if not x._dev]
        for neo in dead_neos:
            neos.remove(neo)
            neo._mutex.unlock()
        if new_neos or dead_neos:
            self._neos = neos + new_neos
            self.changed.emit(self._neos)
