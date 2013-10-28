from ykneomgr import *
from ctypes import POINTER, byref, c_size_t, create_string_buffer
from neoman.device import BaseDevice

DEFAULT_KEY = "404142434445464748494a4b4c4d4e4f".decode('hex')


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

    def unlock(self, key=DEFAULT_KEY):
        check(ykneomgr_authenticate(self._dev, key))

    def set_mode(self, mode):
        check(ykneomgr_modeswitch(self._dev, mode))
        self._mode = mode

    def list_apps(self):
        if self.locked:
            self.unlock()
        applist = create_string_buffer(1024)
        size = c_size_t()
        ykneomgr_applet_list(self._dev, applist, byref(size))
        apps = applist.raw[:size.value - 1].split('\0')

        return apps

    def close(self):
        if hasattr(self, '_dev'):
            ykneomgr_done(self._dev)
            del self._dev


def open_first_device():
    dev = POINTER(ykneomgr_dev)()
    ykneomgr_init(byref(dev))  # TODO: check rc
    check(ykneomgr_discover(dev))

    return CCIDDevice(dev)
