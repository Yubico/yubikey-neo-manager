from ykneomgr import *
from ctypes import POINTER, byref, c_char_p

assert ykneomgr_global_init(0) == 0


NeoHandle = POINTER(ykneomgr_dev)


class YubiKeyNeo(object):

    def __init__(self, dev):
        self._dev = dev
        self._locked = True

    @property
    def locked(self):
        return self._locked

    def unlock(self):
        if ykneomgr_dev_secure(self._dev) != 0:
            raise Exception("Failed to unlock device!")

    def list_apps(self):
        if self.locked:
            self.unlock()
        applist = c_char_p()
        ykneomgr_dev_listapps(self._dev, byref(applist))

        apps = applist.value.split()
        return apps

    def __del__(self):
        ykneomgr_dev_done(self._dev)
        del self._dev


def open_first_neo():
    dev = NeoHandle()
    if ykneomgr_dev_discover(byref(dev)) != 0:
        raise Exception("Unable to open YubiKey NEO!")

    return YubiKeyNeo(dev)
