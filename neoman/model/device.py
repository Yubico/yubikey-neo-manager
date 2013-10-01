class NeoDevice(object):
    def __init__(self, name, serial=None):
        self._name = name
        self._serial = serial

    @property
    def name(self):
        return self._name

    @property
    def serial(self):
        return self._serial

    def __str__(self):
        return self.name
