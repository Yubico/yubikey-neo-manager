# Copyright (c) 2013 Yubico AB
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
from PySide import QtGui, QtCore
from neoman.device import MODE_HID, MODE_CCID, MODE_HID_CCID
from neoman.model.neo import YubiKeyNeo
from neoman.model.applet import get_applet
from collections import OrderedDict

MODES = OrderedDict([
    ("OTP", 0x00),
    ("CCID", 0x01),
    ("CCID with touch eject", 0x81),
    ("OTP+CCID", 0x02),
    ("OTP+CCID with touch eject", 0x82)
])


def name_for_mode(mode):
    return next((n for n, m in MODES.items() if m == mode), None)


class NeoPage(QtGui.QTabWidget):
    neo = QtCore.Signal(YubiKeyNeo)

    def __init__(self):
        super(NeoPage, self).__init__()
        self._neo = None

        settings = SettingsTab()
        self.neo.connect(settings.set_neo)
        self.addTab(settings, "Settings")

        apps = AppsTab(self, 1)
        self.neo.connect(apps.set_neo)
        # self.addTab(apps, "Installed apps")  # TODO: Reenable

    def setNeo(self, neo):
        self._neo = neo
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
        # TODO: Re-add when implemented:
        # layout.addWidget(button)

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
        self._mode_btn.setText(
            "Change connection mode [%s]" % name_for_mode(neo.mode))

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
        current = MODES.keys().index(name_for_mode(self._neo.mode))
        res = QtGui.QInputDialog.getItem(
            self, "Set mode", "Set the connection mode used by your YubiKey "
            "NEO.\nFor this setting to take effect, you will need to unplug, "
            "and re-attach your YubiKey.", MODES.keys(), current, False)
        if res[1]:
            mode = MODES[res[0]]
            if self._neo.mode != mode:
                self._neo.set_mode(mode)
                self._mode_btn.setText(
                    "Change connection mode [%s]" % res[0])

                remove_dialog = QtGui.QMessageBox(self)
                remove_dialog.setWindowTitle("Change mode")
                remove_dialog.setIcon(QtGui.QMessageBox.Information)
                remove_dialog.setText(
                    "\nRemove your YubiKey NEO now.\n")
                remove_dialog.setStandardButtons(QtGui.QMessageBox.NoButton)
                self._neo.removed.connect(remove_dialog.accept)
                remove_dialog.exec_()


class AppsTab(QtGui.QWidget):

    def __init__(self, parent, index):
        super(AppsTab, self).__init__()

        self.parent = parent
        self.index = index

        layout = QtGui.QVBoxLayout()
        self._apps = []
        self._apps_list = QtGui.QListView()
        self._apps_list.setModel(QtGui.QStringListModel([]))
        self._apps_list.setEditTriggers(QtGui.QListView.NoEditTriggers)
        self._apps_list.doubleClicked.connect(self.open_app)
        layout.addWidget(self._apps_list)

        layout.addStretch()
        self.setLayout(layout)

        parent.currentChanged.connect(self.tab_changed)

    def open_app(self, index):
        # print index.data()
        pass

    def tab_changed(self, index):
        if index != self.index:
            return

        try:
            while self._neo.locked:
                try:
                    self._neo.unlock()
                except Exception:
                    pw, ok = QtGui.QInputDialog.getText(
                        self, "Transport key required",
                        "Managing apps on this YubiKey NEO requires a "
                        "password")
                    if not ok:
                        self.parent.setCurrentIndex(0)
                        return
                    self._neo.key = pw

            self._apps = filter(None, map(get_applet, self._neo.list_apps()))
            self._apps_list.model().setStringList(
                map(lambda app: "%s (%s)" % (app.name, app.aid), self._apps))
        except AttributeError:
            pass

    @QtCore.Slot(YubiKeyNeo)
    def set_neo(self, neo):
        self._neo = neo
        if not neo or not neo.has_ccid:
            self.parent.setTabEnabled(self.index, False)
            self.parent.setTabToolTip(self.index, "Requires CCID mode")
            return

        self.parent.setTabEnabled(self.index, True)
        self.parent.setTabToolTip(self.index, None)

        if neo.locked:
            try:
                neo.unlock()
                self._apps = filter(None, map(get_applet, neo.list_apps()))
                self._apps_list.model().setStringList(
                    map(lambda app: "%s (%s)" % (app.name, app.aid), self._apps))
            except:
                pass
