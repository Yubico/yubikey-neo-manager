# Copyright (c) 2013 Yubico AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
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
from PySide.QtGui import QHBoxLayout, QGridLayout, QGroupBox, QLabel, \
    QApplication
from neoman import messages as m
from neoman.configuration_wizard import ConfigWizard
from neoman.device_details import DeviceDetailsDialog
from neoman.legacy_otp import open_otp, slot_status
from neoman.storage import settings
from neoman.exc import ModeSwitchError
from neoman.model.neo import YubiKeyNeo
from neoman.model.applet import Applet
from neoman.model.modes import MODE
from neoman.view.tabs import TabWidgetWithAbout


U2F_URL = "http://www.yubico.com/products/yubikey-hardware/yubikey-neo/" \
          + "yubikey-neo-u2f/"


def get_text(*args, **kwargs):
    flags = (
        QtCore.Qt.WindowTitleHint |
        QtCore.Qt.WindowSystemMenuHint
    )
    kwargs['flags'] = flags
    return QtGui.QInputDialog.getText(*args, **kwargs)


class NeoPage(TabWidgetWithAbout):
    _neo = QtCore.Signal(YubiKeyNeo)
    applet = QtCore.Signal(Applet)

    def __init__(self):
        super(NeoPage, self).__init__()
        self._tabs = []
        self._supported = True

        self._unsupported_tab = UnsupportedTab()

        settings_tab = SettingsWidget()
        self._neo.connect(settings_tab.set_neo)

        grid = QGridLayout()
        grid.addWidget(settings_tab)
        self.setLayout(grid)

        if QtCore.QCoreApplication.instance().devmode:
            apps = AppsTab(self, 1)
            self._neo.connect(apps.set_neo)
            apps.applet.connect(self._set_applet)
            self.addTab(apps, m.installed_apps)

    @QtCore.Slot(YubiKeyNeo)
    def setNeo(self, neo):
        self._supported = neo and neo.supported
        #self.clear()
        for (tab, title) in self._tabs:
            super(NeoPage, self).addTab(tab, title)

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


def link(text):
    return '<a href="#">%s</a>' % text


class SettingsWidget(QtGui.QWidget):
    def __init__(self):
        super(SettingsWidget, self).__init__()

        self._neo = None
        self._name = QtGui.QLabel()
        self._u2f = QtGui.QLabel()
        self._u2f.setOpenExternalLinks(True)

        layout = QtGui.QVBoxLayout()

        layout.addWidget(self.overview_group())
        layout.addWidget(self.slots_group())
        layout.addWidget(self.features_group())
        layout.addWidget(self.connectionmode_group())

        layout.addStretch()
        self.setLayout(layout)

    def overview_group(self):
        grid = QGridLayout()
        grid.addWidget(self._name, 0, 0)
        device_details = QLabel(link('Details'), openExternalLinks=False)
        device_details.linkActivated.connect(self.details_dialog)
        grid.addWidget(device_details, 1, 0)
        group = QGroupBox(flat=True, title='YubiKey edition')
        group.setLayout(grid)
        return group

    def details_dialog(self):
        dialog = DeviceDetailsDialog(self._neo)
        dialog.exec_()

    def features_group(self):
        grid = QGridLayout()
        grid.addWidget(QLabel('FIDO U2F:'), 0, 0)
        self.u2f_supported = QLabel('?')
        grid.addWidget(self.u2f_supported, 0, 1)
        grid.addWidget(QLabel('OpenPGP:'), 1, 0)
        grid.addWidget(QLabel('?'), 1, 1)
        grid.addWidget(QLabel('OATH:'), 2, 0)
        grid.addWidget(QLabel('?'), 2, 1)
        grid.addWidget(QLabel('NFC:'), 3, 0)
        grid.addWidget(QLabel('?'), 3, 1)
        group = QGroupBox(flat=True, title='Fixed features')
        group.setLayout(grid)
        return group

    def slots_group(self):
        grid = QGridLayout()
        grid.addWidget(QLabel('Slot 1 (short press):'), 0, 0)
        self.configure_slot1_link = QLabel(link('Configure'), openExternalLinks=False)
        self.configure_slot1_link.linkActivated.connect(self.configure_slot1)
        grid.addWidget(self.configure_slot1_link, 0, 1)

        grid.addWidget(QLabel('Slot 2 (long press):'), 1, 0)
        self.configure_slot2_link = QLabel(link('Configure'), openExternalLinks=False)
        self.configure_slot2_link.linkActivated.connect(self.configure_slot2)
        grid.addWidget(self.configure_slot2_link, 1, 1)
        group = QGroupBox(flat=True, title='Configurable features')
        group.setLayout(grid)
        return group

    def connectionmode_group(self):
        grid = QGridLayout()
        self.connection_modes = QLabel('N/A')
        grid.addWidget(self.connection_modes, 0, 0)
        self.edit_mode = QLabel(link('Edit'), openExternalLinks=False)
        self.edit_mode.linkActivated.connect(self.change_mode)
        grid.addWidget(self.edit_mode, 0, 1)
        group = QGroupBox(flat=True, title='Active USB protocols')
        group.setLayout(grid)
        return group

    @QtCore.Slot(YubiKeyNeo)
    def set_neo(self, neo):
        self._neo = neo
        if not neo:
            return

        self.edit_mode.setVisible(neo.version[0] >= 3)

        self._name.setText(neo.name)
        if neo.allowed_modes[2]:
            self.u2f_supported.setText('Yes')
        else:
            self.u2f_supported.setText('No')
        self.connection_modes.setText(MODE.name_for_mode(neo.mode))

        self.slot1_configured, slot2_configured = slot_status(open_otp())
        self.configure_slot1_link.setText(link('Reconfigure' if self.slot1_configured else 'Configure'))
        self.configure_slot2_link.setText(link('Reconfigure' if slot2_configured else 'Configure'))

    def configure_slot1(self):
        self.configure_slot(1)

    def configure_slot2(self):
        self.configure_slot(2)

    def configure_slot(self, slot):
        wizard = ConfigWizard(slot, self._neo, self.slot1_configured, self)
        wizard.show()

    def change_mode(self):
        mode = ModeDialog.change_mode(self._neo, self)

        if mode is not None:
            try:
                self._neo.set_mode(mode)
            except ModeSwitchError:
                QtGui.QMessageBox.critical(self, m.mode_error,
                                           m.mode_error_desc)
                return

            self.connection_modes.setText(MODE.name_for_mode(mode))

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

        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

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

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                         QtGui.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._ok = buttons.button(QtGui.QDialogButtonBox.Ok)
        layout.addWidget(buttons)

        self.setWindowTitle(m.change_mode)
        self.setLayout(layout)

        allowed = neo.allowed_modes
        self._otp.setEnabled(allowed[0])
        self._otp.setVisible(allowed[0])
        self._ccid.setEnabled(allowed[1])
        self._ccid.setVisible(allowed[1])
        self._u2f.setEnabled(allowed[2])
        self._u2f.setVisible(allowed[2])
        self.mode = neo.mode

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
        self._otp.setChecked(otp and self._otp.isEnabled())
        self._ccid.setChecked(ccid and self._ccid.isEnabled())
        self._u2f.setChecked(u2f and self._u2f.isEnabled())

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
                    pw, ok = get_text(self, m.key_required, m.key_required_desc)
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
