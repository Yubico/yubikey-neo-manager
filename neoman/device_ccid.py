from ykneomgr import *
from ctypes import byref, c_char_p
from neoman.device import BaseDevice

assert ykneomgr_global_init(0) == 0


def check(status):
    if status != 0:
        raise Exception("Error: %d" % status)


class CCIDDevice(BaseDevice):

    def __init__(self, dev):
        self._dev = dev
        self._locked = True
        self._serial = ykneomgr_get_serialno(dev)
        self._mode = 0xf & ykneomgr_get_mode(dev)
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
        return self._mode

    @property
    def serial(self):
        return self._serial

    @property
    def version(self):
        return self._version

    def unlock(self):
        check(ykneomgr_secure(self._dev))

    def set_mode(self, mode):
        check(ykneomgr_modeswitch(self._dev, mode))
        self._mode = mode

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
    check(ykneomgr_discover(dev))

    return CCIDDevice(dev)
