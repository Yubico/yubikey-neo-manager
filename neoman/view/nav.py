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
from neoman.model.applet import APPLETS


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
                self.model().index(0, 0, self.model().categories['Devices']))
        elif isinstance(self.current, YubiKeyNeo) \
                and self.current not in self.model().neo_list:
            self.current = None
            self.subpage.emit(None)


class NavModel(QtCore.QAbstractItemModel):

    def __init__(self):
        super(NavModel, self).__init__()
        self.categories = {
            "Devices": self.createIndex(0, 0, "Devices"),
            "NEO Apps": self.createIndex(1, 0, "NEO Apps")
        }

        self.applets = APPLETS
        available = QtCore.QCoreApplication.instance().available_neos
        available.changed.connect(self.data_changed)
        self.neo_list = available.get()

    @QtCore.Slot(list)
    def data_changed(self, new_neos):
        parent = self.categories['Devices']

        self.beginRemoveRows(parent, 0, self.rowCount(parent) - 1)
        self.neo_list = []
        self.endRemoveRows()

        self.beginInsertRows(parent, 0, len(new_neos) - 1)
        self.neo_list = new_neos
        self.endInsertRows()

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            node = "Devices" if row == 0 else "NEO Apps"
            return self.categories[node]
        category = parent.internalPointer()
        if category == "Devices":
            return self.createIndex(row, column, self.neo_list[row])
        return self.createIndex(row, column, self.applets[row])

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        node = index.internalPointer()
        if node in self.categories:
            return QtCore.QModelIndex()
        if isinstance(node, YubiKeyNeo):
            return self.categories['Devices']
        return self.categories['NEO Apps']

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return 1  # NEO apps disabled for now 2
        node = parent.internalPointer()
        if node in self.categories:
            return len(self.neo_list if node == "Devices" else self.applets)
        return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return str(index.internalPointer())

    def flags(self, index):
        node = index.internalPointer()
        if node in self.categories:
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
