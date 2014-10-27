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
from functools import partial
from neoman import messages as m
from neoman.storage import settings
from neoman.model.neo import YubiKeyNeo
from neoman.model.applet import Applet
from neoman.model.modes import MODE
from neoman.view.tabs import TabWidgetWithAbout


U2F_URL = "http://www.yubico.com/products/yubikey-hardware/yubikey-neo/" \
    + "yubikey-neo-u2f/"


class NeoPage(TabWidgetWithAbout):
    _neo = QtCore.Signal(YubiKeyNeo)
    applet = QtCore.Signal(Applet)

    def __init__(self):
        super(NeoPage, self).__init__()
        self._tabs = []
        self._supported = True

        self._unsupported_tab = UnsupportedTab()

        settings_tab = SettingsTab()
        self._neo.connect(settings_tab.set_neo)
        self.addTab(settings_tab, m.settings)

        if QtCore.QCoreApplication.instance().devmode:
            apps = AppsTab(self, 1)
            self._neo.connect(apps.set_neo)
            apps.applet.connect(self._set_applet)
            self.addTab(apps, m.installed_apps)

    def addTab(self, tab, title):
        self._tabs.append((tab, title))
        if self._supported:
            super(NeoPage, self).addTab(tab, title)

    @QtCore.Slot(YubiKeyNeo)
    def setNeo(self, neo):
        self._supported = neo and neo.supported
        self.clear()
        if self._supported:
            for (tab, title) in self._tabs:
                super(NeoPage, self).addTab(tab, title)
        else:
            super(NeoPage, self).addTab(self._unsupported_tab, m.settings)

        self._neo.emit(neo)

    @QtCore.Slot(Applet)
    def _set_applet(self, applet):
        self.applet.emit(applet)


class UnsupportedTab(QtGui.QWidget):

    def __init__(self):
        super(UnsupportedTab, self).__init__()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel(m.unsupported_device))
        self.setLayout(layout)


class SettingsTab(QtGui.QWidget):

    def __init__(self):
        super(SettingsTab, self).__init__()

        self._neo = None
        self._name = QtGui.QLabel()
        self._serial = QtGui.QLabel()
        self._firmware = QtGui.QLabel()
        self._u2f = QtGui.QLabel()
        self._u2f.setOpenExternalLinks(True)

        layout = QtGui.QVBoxLayout()

        name_row = QtGui.QHBoxLayout()
        name_row.addWidget(self._name)
        self._name_btn = QtGui.QPushButton(m.change_name)
        self._name_btn.clicked.connect(self.change_name)
        name_row.addWidget(self._name_btn)

        details_row = QtGui.QHBoxLayout()
        details_row.addWidget(self._serial)
        details_row.addWidget(self._firmware)

        self._u2f_row = QtGui.QHBoxLayout()
        self._u2f_row.addWidget(QtGui.QLabel())
        self._u2f_row.addWidget(self._u2f)

        layout.addLayout(name_row)
        layout.addLayout(details_row)
        layout.addLayout(self._u2f_row)

        button = QtGui.QPushButton(m.manage_keys)
        button.clicked.connect(self.manage_keys)
        # TODO: Re-add when implemented:
        # layout.addWidget(button)

        self._mode_btn = QtGui.QPushButton(m.change_mode)
        self._mode_btn.clicked.connect(self.change_mode)
        layout.addWidget(self._mode_btn)

        mode_note = QtGui.QLabel(m.note_1 % m.mode_note)
        mode_note.setWordWrap(True)
        layout.addWidget(mode_note)

        layout.addStretch()
        self.setLayout(layout)

    @QtCore.Slot(YubiKeyNeo)
    def set_neo(self, neo):
        self._neo = neo
        if not neo:
            return

        self._name_btn.setDisabled(neo.serial is None)
        self._name.setText(m.name_1 % neo.name)
        self._serial.setText(m.serial_1 % neo.serial)
        show_firmware = neo.version != (0, 0, 0)
        self._u2f_row.setDirection(
            QtGui.QBoxLayout.LeftToRight if show_firmware else
            QtGui.QBoxLayout.RightToLeft)
        self._firmware.setVisible(show_firmware)
        self._firmware.setText(m.firmware_1 % '.'.join(map(str, neo.version)))
        if neo.u2f_capable:
            self._u2f.setText(m.u2f_1 % m.u2f_supported)
        else:
            self._u2f.setText(m.u2f_1 % m.u2f_not_supported_1 % U2F_URL)
        self._mode_btn.setText(m.change_mode_1 % MODE.name_for_mode(neo.mode))

    def change_name(self):
        name, ok = QtGui.QInputDialog.getText(
            self, m.name, m.change_name_desc, text=self._neo.name)
        if ok:
            self._neo.name = name
            self._name.setText(m.name_1 % name)

    def manage_keys(self):
        print m.manage_keys

    def change_mode(self):
        mode = ModeDialog.change_mode(self._neo, self)

        if mode is not None:
            self._neo.set_mode(mode)
            self._mode_btn.setText(m.change_mode_1 % MODE.name_for_mode(mode))

            remove_dialog = QtGui.QMessageBox(self)
            remove_dialog.setWindowTitle(m.change_mode)
            remove_dialog.setIcon(QtGui.QMessageBox.Information)
            remove_dialog.setText(m.remove_device)
            remove_dialog.setStandardButtons(QtGui.QMessageBox.NoButton)
            self._neo.removed.connect(remove_dialog.accept)
            remove_dialog.exec_()


class ModeDialog(QtGui.QDialog):
    def __init__(self, neo, parent=None):
        super(ModeDialog, self).__init__(parent)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel(m.change_mode_desc))

        boxes = QtGui.QHBoxLayout()
        self._otp = QtGui.QCheckBox(m.otp)
        self._otp.clicked.connect(self._state_changed)
        boxes.addWidget(self._otp)
        self._ccid = QtGui.QCheckBox(m.ccid)
        self._ccid.clicked.connect(self._state_changed)
        boxes.addWidget(self._ccid)
        self._u2f = QtGui.QCheckBox(m.u2f)
        self._u2f.clicked.connect(self._state_changed)
        boxes.addWidget(self._u2f)
        layout.addLayout(boxes)

        # Disable OTP in combination with U2F
        # Remove the rest of this method to re-enable.
        if neo.u2f_capable:
            note = QtGui.QLabel(m.note_1 % m.otp_u2f_disabled)

            def otp_clicked():
                if self._otp.isChecked() and self._u2f.isChecked():
                    note.setStyleSheet("QLabel { color: red; }")
                    self._u2f.setChecked(False)
            self._otp.clicked.connect(otp_clicked)

            def u2f_clicked():
                if self._otp.isChecked() and self._u2f.isChecked():
                    note.setStyleSheet("QLabel { color: red; }")
                    self._otp.setChecked(False)
            self._u2f.clicked.connect(u2f_clicked)
            layout.addWidget(note)
        # End Disable OTP in combination with U2F

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                         QtGui.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._ok = buttons.button(QtGui.QDialogButtonBox.Ok)
        layout.addWidget(buttons)

        self.setWindowTitle(m.change_mode)
        self.setLayout(layout)

        self.mode = neo.mode
        self.has_u2f = neo.u2f_capable

    def _state_changed(self):
        self._ok.setDisabled(not any(self.flags))

    @property
    def flags(self):
        return self._otp.isChecked(), self._ccid.isChecked(), \
            self._u2f.isChecked()

    @property
    def mode(self):
        return MODE.mode_for_flags(*self.flags)

    @mode.setter
    def mode(self, value):
        otp, ccid, u2f, touch_eject = MODE.flags_for_mode(value)
        self._otp.setChecked(otp)
        self._ccid.setChecked(ccid)
        self._u2f.setChecked(u2f)

    @property
    def has_u2f(self):
        return self._u2f.isVisible()

    @has_u2f.setter
    def has_u2f(self, value):
        self._u2f.setVisible(value)

    @classmethod
    def change_mode(cls, neo, parent=None):
        dialog = cls(neo, parent)
        if dialog.exec_():
            mode = dialog.mode
            legacy = neo.version < (3, 3, 0)
            if legacy and mode == 2:  # Always set 82 instead of 2
                mode = 0x82
            return mode
        else:
            return None


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
                except Exception as e:
                    del self._neo.key
                    print e
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
