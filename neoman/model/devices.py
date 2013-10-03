from PySide import QtCore
from neoman.device import open_first_device


class DeviceWrapper(object):

    def __init__(self, delegate):
        self._delegate = delegate

    @property
    def device(self):
        return self._delegate

    def __str__(self):
        return str(self._delegate)


class Devices(QtCore.QObject):
    changed = QtCore.Signal(list)

    def __init__(self):
        super(Devices, self).__init__()

        dev = open_first_device()
        self._wrapper = DeviceWrapper(dev) if dev else None
        self.startTimer(1000)

    def __len__(self):
        return 1 if self._wrapper else 0

    def __getitem__(self, index):
        return self._wrapper

    def __iter__(self):
        if self._wrapper:
            yield self._wrapper

    def timerEvent(self, event):
        if self._wrapper:
            self._wrapper.device.close()
            old_dev = self._wrapper.device
        else:
            old_dev = None

        new_dev = open_first_device()
        if not old_dev and not new_dev:
            return

        if new_dev:
            if self._wrapper:
                self._wrapper._delegate = new_dev
            else:
                self._wrapper = DeviceWrapper(new_dev)
        else:
            self._wrapper = None

        if old_dev and new_dev:
            # Check if same:
            if old_dev.serial == new_dev.serial:
                return

        print 'New devices: %r' % self._wrapper
        self.changed.emit(self)
