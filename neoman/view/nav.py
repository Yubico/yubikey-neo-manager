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
from neoman.model.neo import YubiKeyNeo
from neoman.model.applet import Applet
from neoman import messages as m


class NavTree(QtGui.QTreeView):
    subpage = QtCore.Signal(object)

    def __init__(self):
        super(NavTree, self).__init__()

        self.setHeaderHidden(True)
        self.setModel(NavModel())
        self.expandAll()

        self.current = None

        self.model().rowsInserted.connect(self._data_changed)
        self._data_changed()

    @QtCore.Slot(YubiKeyNeo)
    @QtCore.Slot(Applet)
    def setCurrent(self, current):
        self.current = current
        try:
            if isinstance(current, YubiKeyNeo):
                neo_index = self.model().neo_list.index(current)
                self.setCurrentIndex(
                    self.model().index(
                        neo_index, 0, self.model().categories[m.devices]))
            elif isinstance(current, Applet):
                applet_index = self.model().applets.index(current)
                self.setCurrentIndex(
                    self.model().index(
                        applet_index, 0, self.model().categories[m.apps]))
        except:
            self.clearSelection()

    def setCurrentIndex(self, index):
        super(NavTree, self).setCurrentIndex(index)
        self.model().refresh_icons(index)

    def currentChanged(self, current, previous):
        if current.flags() & QtCore.Qt.ItemIsSelectable:
            self.current = current.internalPointer()
            self.subpage.emit(self.current)
        elif not self.model().neo_list:
            self.current = None
            self.subpage.emit(None)
        elif isinstance(self.current, YubiKeyNeo):
            pass
        else:
            self.current = self.model().neo_list[0]
            self.subpage.emit(self.current)

    def _data_changed(self):
        if not self.current and self.model().neo_list:
            self.setCurrentIndex(
                self.model().index(0, 0, self.model().categories[m.devices]))
        elif isinstance(self.current, YubiKeyNeo) \
                and self.current not in self.model().neo_list:
            self.current = None
            self.subpage.emit(None)


class NavModel(QtCore.QAbstractItemModel):

    def __init__(self):
        super(NavModel, self).__init__()
        self.categories = {
            m.devices: self.createIndex(0, 0, m.devices),
            m.apps: self.createIndex(1, 0, m.apps)
        }

        self.refresh_icons()

        self.applets = []
        available = QtCore.QCoreApplication.instance().available_neos
        available.changed.connect(self.data_changed)
        self.neo_list = available.get()
        self._update_applets()

    def refresh_icons(self, index=None):
        if index and index.isValid():
            self._get_icon(index, True)
        else:
            self._icons = {m.devices: {}, m.apps: {}}

    @QtCore.Slot(list)
    def data_changed(self, new_neos):
        parent = self.categories[m.devices]

        self.beginRemoveRows(parent, 0, self.rowCount(parent) - 1)
        self.neo_list = []
        self.endRemoveRows()

        self.beginInsertRows(parent, 0, len(new_neos) - 1)
        self.neo_list = new_neos
        self.endInsertRows()
        self._update_applets()

        self.refresh_icons()

    def _update_applets(self):
        parent = self.categories[m.apps]

        self.beginRemoveRows(parent, 0, self.rowCount(parent) - 1)
        self.applets = []
        self.endRemoveRows()

        new_applets = []
        installed = {app for neo in self.neo_list for app in neo.list_apps()}
        appletmanager = QtCore.QCoreApplication.instance().appletmanager
        if QtCore.QCoreApplication.instance().devmode:
            new_applets = appletmanager.get_applets()
        else:
            for applet in appletmanager.get_applets():
                if any([aid.startswith(applet.aid) for aid in installed]):
                    new_applets.append(applet)

        self.beginInsertRows(parent, 0, len(new_applets) - 1)
        self.applets = new_applets
        self.endInsertRows()

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            node = m.devices if row == 0 else m.apps
            return self.categories[node]
        category = parent.internalPointer()
        if category == m.devices:
            return self.createIndex(row, column, self.neo_list[row])
        return self.createIndex(row, column, self.applets[row])

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        node = index.internalPointer()
        if node in self.categories:
            return QtCore.QModelIndex()
        if isinstance(node, YubiKeyNeo):
            return self.categories[m.devices]
        return self.categories[m.apps]

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return 2
        node = parent.internalPointer()
        if node in self.categories:
            return len(self.neo_list if node == m.devices else self.applets)
        return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(index.internalPointer())
            elif QtCore.QCoreApplication.instance().devmode and \
                    role == QtCore.Qt.DecorationRole:
                return self._get_icon(index)

    def _get_icon(self, index, force_refresh=False):
        parent = index.parent()
        if not parent.isValid():
            return None
        category = parent.internalPointer()
        if force_refresh or index.row() not in self._icons[category]:
            self._icons[category][index.row()] = self._build_icon(index)
        return self._icons[category][index.row()]

    def _build_icon(self, index):
        item = index.internalPointer()
        icon_template = ':/icon_%s.png'
        if isinstance(item, Applet):
            all_installed = bool(self.neo_list)
            some_installed = False
            for neo in self.neo_list:
                if any((aid.startswith(item.aid) for aid in neo.list_apps())):
                    some_installed = True
                else:
                    all_installed = False
            if all_installed:
                return QtGui.QPixmap(icon_template % 'installed')
            elif some_installed:
                return QtGui.QPixmap(icon_template % 'some_installed')
            else:
                return QtGui.QPixmap(icon_template % 'not_installed')

    def flags(self, index):
        node = index.internalPointer()
        if node in self.categories:
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
