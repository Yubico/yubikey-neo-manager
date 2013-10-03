MODE_HID = 0
MODE_CCID = 1
MODE_HID_CCID = 2


class BaseDevice(object):

    @property
    def mode(self):
        raise NotImplementedError()

    @property
    def has_ccid(self):
        return self.mode in [MODE_CCID, MODE_HID_CCID]

    @property
    def serial(self):
        raise NotImplementedError()

    @property
    def version(self):
        raise NotImplementedError()

    def __del__(self):
        if hasattr(self, 'close'):
            self.close()

    def __str__(self):
        return "NEO[mode=%d, serial=%s]" % (self.mode, self.serial)


def open_first_device():
    try:
        from neoman.device_ccid import open_first_device as open_ccid
        return open_ccid()
    except:
        try:
            from neoman.device_hid import open_first_device as open_hid
            return open_hid()
        except:
            return None
