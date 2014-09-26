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
from neoman.device import open_all_devices
from neoman.storage import settings
from functools import wraps

DEFAULT_KEY = "404142434445464748494a4b4c4d4e4f"


def with_mutex(mutex, func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            mutex.lock()
            return func(*args, **kwargs)
        finally:
            mutex.unlock()
    return inner


class YubiKeyNeo(QtCore.QObject):
    removed = QtCore.Signal()

    def __init__(self, device):
        super(YubiKeyNeo, self).__init__()

        self._mutex = QtCore.QMutex(QtCore.QMutex.Recursive)

        self._serial = device.serial
        self._version = device.version
        self._apps = None

        self._group = self._serial if self._serial else "NOSERIAL"

        self._set_device(device)

    def _set_device(self, device):
        if self.serial != device.serial or self.version != device.version:
            print self.serial, self.version, device.serial, device.version
            raise ValueError("New device must have same serial/version.")
        self._dev = device
        self._mode = device.mode
        self._default_name = device.default_name
        #self._apps = None
        if device.has_ccid:
            device.key = self.key.decode('hex')

    def __setitem__(self, key, value):
        settings.setValue('%s/%s' % (self._group, key), value)

    def __delitem__(self, key):
        settings.remove('%s/%s' % (self._group, key))

    def __getitem__(self, key):
        return self.get(key)

    def __nonzero__(self):
        return True

    def __len__(self):
        try:
            settings.beginGroup('%s' % self._group)
            return len(settings.allKeys())
        finally:
            settings.endGroup()

    def __getattr__(self, name):
        try:
            self._mutex.lock()
            if not self._dev:
                raise AttributeError(name)
            attr = getattr(self._dev, name)
            if hasattr(attr, '__call__'):
                attr = with_mutex(self._mutex, attr)
            return attr
        finally:
            self._mutex.unlock()

    def __delattr__(self, key):
        del self[key]

    def get(self, key, default=None):
        return settings.value('%s/%s' % (self._group, key), default)

    @property
    def name(self):
        return self.get('name', self._default_name)

    @name.setter
    def name(self, new_name):
        self['name'] = new_name

    @property
    def key(self):
        return self.get('key', DEFAULT_KEY)

    @key.setter
    def key(self, new_key):
        self['key'] = new_key
        try:
            self._mutex.lock()
            self._dev.key = new_key.decode('hex')
        finally:
            self._mutex.unlock()

    def set_key(self, new_key):
        try:
            self._mutex.lock()
            print "NOT IMPLEMENTED"
            #TODO: change key
        finally:
            self._mutex.unlock()

    @property
    def has_ccid(self):
        try:
            self._mutex.lock()
            return self._dev and self._dev.has_ccid
        finally:
            self._mutex.unlock()


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
        return self.name

    def list_apps(self):
        try:
            self._mutex.lock()
            if not self.has_ccid:
                return []
            if self._apps is None:
                apps = []
                appletmanager = QtCore.QCoreApplication.instance().appletmanager
                for applet in appletmanager.get_applets():
                    installed, version = applet.get_status(self)
                    if installed:
                        apps.append(applet.aid)
                self._apps = apps
            return self._apps
        finally:
            self._mutex.unlock()


class AvailableNeos(QtCore.QThread):
    changed = QtCore.Signal(list)

    def __init__(self):
        super(AvailableNeos, self).__init__()

        self._mutex = QtCore.QMutex()

        self._neos = []
        self._running = True

    def stop(self):
        self._running = False
        self.wait()

    def get(self):
        try:
            self._mutex.lock()
            return self._neos[:]
        finally:
            self._mutex.unlock()

    def run(self):
        self.discover_devices()  # Discover initial devices.
        while self._running:
            if QtGui.QApplication.activeWindow():  # Only if we have focus
                self.discover_devices()
            self.msleep(1000)

    def discover_devices(self):
        neos = self.get()
        existing_devs = []
        for neo in neos:
            if neo._dev:
                neo._mutex.lock()
                existing_devs.append(neo._dev)
                neo._dev = None

        discovered = open_all_devices(existing_devs)

        new_neos = []
        dead_neos = neos[:]
        for dev in discovered:
            for neo in dead_neos[:]:
                if dev.serial == neo.serial:
                    neo._set_device(dev)
                    neo._mutex.unlock()
                    dead_neos.remove(neo)
                    break
            else:
                new_neos.append(YubiKeyNeo(dev))

        for neo in dead_neos:
            neos.remove(neo)
            neo.removed.emit()
            neo._mutex.unlock()
        if new_neos or dead_neos:
            self._mutex.lock()
            self._neos = neos + new_neos
            neos_copy = self._neos[:]
            self._mutex.unlock()
            self.changed.emit(neos_copy)
