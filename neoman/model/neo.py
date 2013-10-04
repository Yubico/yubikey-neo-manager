from PySide import QtCore
from neoman.device import open_first_device
from neoman.storage import settings


class YubiKeyNeo(QtCore.QObject):

    def __init__(self, device):
        super(YubiKeyNeo, self).__init__()

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

    def get(self, key, default=None):
        return settings.value('%s/%s' % (self._group, key), default)

    @property
    def device(self):
        return self._dev

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


class AvailableNeos(QtCore.QObject):
    changed = QtCore.Signal(list)

    def __init__(self):
        super(AvailableNeos, self).__init__()

        self._neos = []
        self.discover_devices()
        self.startTimer(1000)

    @property
    def neos(self):
        return self._neos

    def discover_devices(self):
        neos = self._neos[:]
        for neo in neos:
            del neo._dev

        single = open_first_device()
        discovered = [single] if single else []

        new_neos = []
        for dev in discovered:
            for neo in neos:
                if dev.serial == neo.serial:
                    neo._set_device(dev)
                    break
            else:
                new_neos.append(YubiKeyNeo(dev))

        dead_neos = [x for x in neos if not hasattr(x, '_dev')]
        for neo in dead_neos:
            neos.remove(neo)
        if new_neos or dead_neos:
            self._neos = neos + new_neos
            self.changed.emit(self._neos)

    def timerEvent(self, event):
        self.discover_devices()
