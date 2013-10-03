from PySide import QtGui, QtCore
from neoman.model.devices import DeviceWrapper


class DeviceWidget(QtGui.QTabWidget):

    def __init__(self):
        super(DeviceWidget, self).__init__()
        self.add_settings_tab()
        self.add_apps_tab()

    def setDevice(self, dev):
        self._dev = dev
        self._name.setText("Name: %s" % dev.device.serial)
        self._serial.setText("Serial number: %s" % dev.device.serial)
        self._firmware.setText("Firmware version: %s" % dev.device.version)
        #self.device.emit(dev)

    def getDevice(self):
        return self._dev

    device = QtCore.Property(DeviceWrapper, getDevice, setDevice)

    def change_name(self):
        print "Change name"

    def manage_keys(self):
        print "Manage transport keys"

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


class QDevice(QtGui.QTabWidget):

    def __init__(self, device):
        super(QDevice, self).__init__()
        self._dev = device
        self.add_settings_tab()
        self.add_apps_tab()

    def add_settings_tab(self):
        settings = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel("Name"))
        layout.addWidget(QtGui.QLabel(self._dev.name))

        layout.addWidget(QtGui.QLabel("Serial"))
        layout.addWidget(QtGui.QLabel(self._dev.serial))

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
