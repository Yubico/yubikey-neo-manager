from ykneomgr import *
from ctypes import byref, c_char_p
from neoman.device import BaseDevice, MODE_CCID

assert ykneomgr_global_init(0) == 0


class CCIDDevice(BaseDevice):

    def __init__(self, dev):
        self._dev = dev
        self._locked = True
        self._serial = ykneomgr_get_serialno(dev)
        self._version = [
            ykneomgr_get_version_major(dev),
            ykneomgr_get_version_minor(dev),
            ykneomgr_get_version_build(dev)
        ]

    @property
    def locked(self):
        return self._locked

    @property
    def mode(self):
        return MODE_CCID

    @property
    def serial(self):
        return self._serial

    @property
    def version(self):
        return self._version

    def unlock(self):
        status = ykneomgr_secure(self._dev)
        if status != 0:
            raise Exception("Failed to unlock device. Error: %d" % status)

    def list_apps(self):
        if self.locked:
            self.unlock()
        applist = c_char_p()
        ykneomgr_listapps(self._dev, byref(applist))

        apps = applist.value.split()
        return apps

    def close(self):
        if hasattr(self, '_dev'):
            ykneomgr_done(self._dev)
            del self._dev


def open_first_device():
    dev = ykneomgr_init()
    status = ykneomgr_discover(dev)
    if status != 0:
        raise Exception("Unable to open YubiKey NEO. Error: %d", status)

    return CCIDDevice(dev)
