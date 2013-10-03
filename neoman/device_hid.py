from ykpers import *
from ctypes import byref, c_uint
from neoman.device import BaseDevice, MODE_HID

assert yk_init()


class HIDDevice(BaseDevice):

    def __init__(self, dev):
        self._dev = dev

        ser = c_uint()
        self._serial = ser.value if yk_get_serial(dev, 0, 0, byref(ser)) else 0

        status = ykds_alloc()
        try:
            if yk_get_status(dev, status):
                self._version = [
                    ykds_version_major(status),
                    ykds_version_minor(status),
                    ykds_version_build(status)
                ]
            else:
                self._version = [0, 0, 0]
        finally:
            ykds_free(status)

    @property
    def mode(self):
        return MODE_HID

    @property
    def serial(self):
        return self._serial

    @property
    def version(self):
        return self._version

    def set_mode(self, mode):
        if self.version[0] < 3:
            raise Exception("Mode Switching requires version >= 3")

        config = ykp_alloc_device_config()
        ykp_set_device_mode(config, mode)
        if not yk_write_device_config(self._dev, config):
            raise Exception("Failed writing device config!")
        else:
            print "Mode switched. Re-insert for this to take effect."
        ykp_free_device_config(config)

    def close(self):
        if hasattr(self, '_dev'):
            yk_close_key(self._dev)
            del self._dev


def open_first_device():
    dev = yk_open_first_key()
    if not dev:
        raise Exception("Unable to open YubiKey!")

    return HIDDevice(dev)
