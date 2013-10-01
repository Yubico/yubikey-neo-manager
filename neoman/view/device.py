from PySide import QtGui


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
