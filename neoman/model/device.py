class NeoDevice(object):

    def __init__(self, name, serial=None, firmware=None):
        self._name = name
        self._serial = serial
        self._firmware = firmware

    @property
    def name(self):
        return self._name

    @property
    def serial(self):
        return self._serial or "<unset>"

    @property
    def firmware(self):
        return self._firmware or "<unknown>"

    def __str__(self):
        return self.name
