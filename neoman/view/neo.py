from PySide import QtGui, QtCore
from neoman.device import MODE_HID, MODE_CCID, MODE_HID_CCID
from neoman.model.neo import YubiKeyNeo


MODES = ["OTP", "CCID", "OTP+CCID"]
MODE_NAMES = {
    MODE_HID: MODES[0],
    MODE_CCID: MODES[1],
    MODE_HID_CCID: MODES[2]
}


class NeoPage(QtGui.QTabWidget):
    neo = QtCore.Signal(YubiKeyNeo)

    def __init__(self):
        super(NeoPage, self).__init__()
        self._neo = None

        self.add_settings_tab()
        self.add_apps_tab()

    def setNeo(self, neo):
        if self._neo:
            self._neo.removed.disconnect(self.neo_removed)
        self._neo = neo
        self._name.setText("Name: %s" % neo.name)
        self._serial.setText("Serial number: %s" % neo.serial)
        self._firmware.setText("Firmware version: %s" %
                               '.'.join(map(str, neo.version)))
        neo.removed.connect(self.neo_removed)
        self.neo.emit(neo)

    def getNeo(self):
        return self._neo

    def neo_removed(self):
        self._neo = None
        self.neo.emit(None)

    def change_name(self):
        name, ok = QtGui.QInputDialog.getText(
            self, "Name", "Change the name of the device.",
            text=self._neo.name)
        if ok:
            self._neo.name = name
            self._name.setText("Name: %s" % name)

    def manage_keys(self):
        print "Manage transport keys"

    def change_mode(self):
        current = MODES.index(MODE_NAMES[self._neo.mode])
        res = QtGui.QInputDialog.getItem(
            self, "Set mode", "Set the connection mode used by your YubiKey "
            "NEO.\nFor this setting to take effect, you will need to unplug, "
            "and re-attach your YubiKey.", MODES, current, False)
        if res[1]:
            res = next((mode for mode, name in MODE_NAMES.items()
                        if name == res[0]))
            if self._neo.mode != res:
                self._neo.device.set_mode(res)

    def add_settings_tab(self):
        self._name = QtGui.QLabel()
        self._serial = QtGui.QLabel()
        self._firmware = QtGui.QLabel()

        settings = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()

        name_row = QtGui.QHBoxLayout()
        name_row.addWidget(self._name)
        button = QtGui.QPushButton("Change name")
        button.clicked.connect(self.change_name)
        name_row.addWidget(button)

        details_row = QtGui.QHBoxLayout()
        details_row.addWidget(self._serial)
        details_row.addWidget(self._firmware)

        layout.addLayout(name_row)
        layout.addLayout(details_row)

        button = QtGui.QPushButton("Manage transport keys")
        button.clicked.connect(self.manage_keys)
        layout.addWidget(button)

        button = QtGui.QPushButton("Change connection mode")
        button.clicked.connect(self.change_mode)
        layout.addWidget(button)

        layout.addStretch()
        settings.setLayout(layout)
        self.addTab(settings, "Settings")

    def add_apps_tab(self):
        apps = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()

        layout.addWidget(QtGui.QLabel("No apps installed!"))

        layout.addStretch()
        apps.setLayout(layout)
        self.addTab(apps, "Installed apps")
