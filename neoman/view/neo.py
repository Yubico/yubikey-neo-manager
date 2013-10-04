from PySide import QtGui, QtCore
from neoman.device import MODE_HID, MODE_CCID, MODE_HID_CCID
from neoman.model.neo import YubiKeyNeo
from neoman.model.applet import get_applet


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

        settings = SettingsTab()
        self.neo.connect(settings.set_neo)
        self.addTab(settings, "Settings")

        apps = AppsTab()
        self.neo.connect(apps.set_neo)
        self.addTab(apps, "Installed apps")

    def setNeo(self, neo):
        self._neo = neo
        if neo:
            has_ccid = neo.mode in [MODE_CCID, MODE_HID_CCID]
            self.setTabEnabled(1, has_ccid)
            self.setTabToolTip(1, None if has_ccid else "Requires CCID mode")
        self.neo.emit(neo)

    def getNeo(self):
        return self._neo


class SettingsTab(QtGui.QWidget):

    def __init__(self):
        super(SettingsTab, self).__init__()

        self._neo = None
        self._name = QtGui.QLabel()
        self._serial = QtGui.QLabel()
        self._firmware = QtGui.QLabel()

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

        self._mode_btn = QtGui.QPushButton("Change connection mode")
        self._mode_btn.clicked.connect(self.change_mode)
        layout.addWidget(self._mode_btn)

        layout.addStretch()
        self.setLayout(layout)

    @QtCore.Slot(YubiKeyNeo)
    def set_neo(self, neo):
        self._neo = neo
        if not neo:
            return

        self._name.setText("Name: %s" % neo.name)
        self._serial.setText("Serial number: %s" % neo.serial)
        self._firmware.setText("Firmware version: %s" %
                               '.'.join(map(str, neo.version)))
        self._mode_btn.setText("Change connection mode [%s]" % MODES[neo.mode])

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
            m = next((mode for mode, name in MODE_NAMES.items()
                      if name == res[0]))
            if self._neo.mode != m:
                self._neo.device.set_mode(m)
                self._mode_btn.setText(
                    "Change connection mode [%s]" % res[0])


class AppsTab(QtGui.QWidget):

    def __init__(self):
        super(AppsTab, self).__init__()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel("No apps installed!"))

        layout.addStretch()
        self.setLayout(layout)

    @QtCore.Slot(YubiKeyNeo)
    def set_neo(self, neo):
        self._neo = neo
        if not neo or neo.mode not in [MODE_CCID, MODE_HID_CCID]:
            return

        self._apps = map(get_applet, neo.device.list_apps())
        for app in self._apps:
            self.layout().addWidget(QtGui.QLabel(app.name))
