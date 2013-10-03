from PySide import QtCore
from neoman.device import open_first_device

name_store = {}


class YubiKeyNeo(QtCore.QObject):
    removed = QtCore.Signal()

    def __init__(self, device):
        super(YubiKeyNeo, self).__init__()

        self._dev = device
        self._name = name_store.get(device.serial,
                                    "YubiKey %s" % device.serial)
        self._mode = device.mode
        self._serial = device.serial
        self._version = device.version

    def _set_device(self, device):
        assert self.serial == device.serial
        assert self.version == device.version
        self._dev = device
        self._mode = device.mode

    @property
    def device(self):
        return self._dev

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        name_store[self.serial] = new_name

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
            neo.removed.emit()
        if new_neos or dead_neos:
            self._neos = neos + new_neos
            self.changed.emit(self._neos)

    def timerEvent(self, event):
        self.discover_devices()
