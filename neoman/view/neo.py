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
import os
from PySide import QtGui, QtCore
from collections import OrderedDict
from functools import partial
from neoman import messages as m
from neoman.storage import settings
from neoman.model.neo import YubiKeyNeo
from neoman.model.applet import Applet

MODES = OrderedDict([
    (m.hid, 0x00),
    (m.ccid, 0x01),
    (m.ccid_touch_eject, 0x81),
    (m.hid_ccid, 0x02),
    (m.hid_ccid_touch_eject, 0x82)
])


def name_for_mode(mode):
    return next((n for n, md in MODES.items() if md == mode), None)


class NeoPage(QtGui.QTabWidget):
    _neo = QtCore.Signal(YubiKeyNeo)
    applet = QtCore.Signal(Applet)

    def __init__(self):
        super(NeoPage, self).__init__()

        settings_tab = SettingsTab()
        self._neo.connect(settings_tab.set_neo)
        self.addTab(settings_tab, m.settings)

        apps = AppsTab(self, 1)
        self._neo.connect(apps.set_neo)
        apps.applet.connect(self._set_applet)
        self.addTab(apps, m.installed_apps)

    @QtCore.Slot(YubiKeyNeo)
    def setNeo(self, neo):
        self._neo.emit(neo)

    @QtCore.Slot(Applet)
    def _set_applet(self, applet):
        self.applet.emit(applet)


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
        button = QtGui.QPushButton(m.change_name)
        button.clicked.connect(self.change_name)
        name_row.addWidget(button)

        details_row = QtGui.QHBoxLayout()
        details_row.addWidget(self._serial)
        details_row.addWidget(self._firmware)

        layout.addLayout(name_row)
        layout.addLayout(details_row)

        button = QtGui.QPushButton(m.manage_keys)
        button.clicked.connect(self.manage_keys)
        # TODO: Re-add when implemented:
        # layout.addWidget(button)

        self._mode_btn = QtGui.QPushButton(m.change_mode)
        self._mode_btn.clicked.connect(self.change_mode)
        layout.addWidget(self._mode_btn)

        layout.addStretch()
        self.setLayout(layout)

    @QtCore.Slot(YubiKeyNeo)
    def set_neo(self, neo):
        self._neo = neo
        if not neo:
            return

        self._name.setText(m.name_1 % neo.name)
        self._serial.setText(m.serial_1 % neo.serial)
        self._firmware.setText(m.firmware_1 % '.'.join(map(str, neo.version)))
        self._mode_btn.setText(m.change_mode_1 % name_for_mode(neo.mode))

    def change_name(self):
        name, ok = QtGui.QInputDialog.getText(
            self, m.name, m.change_name_desc, text=self._neo.name)
        if ok:
            self._neo.name = name
            self._name.setText(m.name_1 % name)

    def manage_keys(self):
        print m.manage_keys

    def change_mode(self):
        current = MODES.keys().index(name_for_mode(self._neo.mode))
        res = QtGui.QInputDialog.getItem(
            self, m.change_mode, m.change_mode_desc, MODES.keys(), current,
            False)
        if res[1]:
            mode = MODES[res[0]]
            if self._neo.mode != mode:
                self._neo.set_mode(mode)
                self._mode_btn.setText(m.change_mode_1 % res[0])

                remove_dialog = QtGui.QMessageBox(self)
                remove_dialog.setWindowTitle(m.change_mode)
                remove_dialog.setIcon(QtGui.QMessageBox.Information)
                remove_dialog.setText(m.remove_device)
                remove_dialog.setStandardButtons(QtGui.QMessageBox.NoButton)
                self._neo.removed.connect(remove_dialog.accept)
                remove_dialog.exec_()


class AppsTab(QtGui.QWidget):
    applet = QtCore.Signal(Applet)

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

        self._install_cap_btn = QtGui.QPushButton(m.install_cap)
        self._install_cap_btn.clicked.connect(self.install_cap)
        layout.addWidget(self._install_cap_btn)

        layout.addStretch()
        self.setLayout(layout)

        parent.currentChanged.connect(self.tab_changed)

    def install_cap(self):
        path = settings.value('filepicker/path', None)
        (cap, _) = QtGui.QFileDialog.getOpenFileName(self, m.select_cap,
                                                     path, "*.cap")
        if not cap:
            return
        settings.setValue('filepicker/path', os.path.dirname(cap))
        worker = QtCore.QCoreApplication.instance().worker
        self._cap = os.path.basename(cap)
        worker.post(m.installing, partial(self._neo.install_app, cap),
                    self.install_done)

    @QtCore.Slot(object)
    def install_done(self, status):
        if status:
            print status
            QtGui.QMessageBox.warning(self, m.error_installing,
                                      m.error_installing_1 % self._cap)
        self.set_neo(self._neo)

    def open_app(self, index):
        readable = index.data()
        aid = readable[readable.rindex('(') + 1:readable.rindex(')')]
        appletmanager = QtCore.QCoreApplication.instance().appletmanager
        self.applet.emit(appletmanager.get_applet(aid))

    def tab_changed(self, index):
        if index != self.index:
            return

        try:
            while self._neo.locked:
                try:
                    self._neo.unlock()
                except Exception:
                    pw, ok = QtGui.QInputDialog.getText(
                        self, m.key_required, m.key_required_desc)
                    if not ok:
                        self.parent.setCurrentIndex(0)
                        return
                    self._neo.key = pw

            appletmanager = QtCore.QCoreApplication.instance().appletmanager
            self._apps = filter(None, map(appletmanager.get_applet,
                                          self._neo.list_apps()))
            self._apps_list.model().setStringList(
                map(lambda app: "%s (%s)" % (app.name, app.aid), self._apps))
        except AttributeError:
            pass

    @QtCore.Slot(YubiKeyNeo)
    def set_neo(self, neo):
        self._neo = neo
        if not neo or not neo.has_ccid:
            self.parent.setTabEnabled(self.index, False)
            self.parent.setTabToolTip(self.index, m.requires_ccid)
            return

        self.parent.setTabEnabled(self.index, True)
        self.parent.setTabToolTip(self.index, None)

        if neo.locked:
            try:
                neo.unlock()
            except:
                return

        appletmanager = QtCore.QCoreApplication.instance().appletmanager
        self._apps = filter(None, map(appletmanager.get_applet,
                                      neo.list_apps()))
        self._apps_list.model().setStringList(
            map(lambda app: "%s (%s)" % (app.name, app.aid), self._apps))
