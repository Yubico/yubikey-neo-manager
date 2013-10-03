from PySide import QtGui, QtCore
from neoman.model.neo import AvailableNeos, YubiKeyNeo


class NavTree(QtGui.QTreeView):

    def __init__(self):
        super(NavTree, self).__init__()

        self.setHeaderHidden(True)
        self.setModel(NavModel())
        self.expandAll()

    subpage = QtCore.Signal(object)

    def currentChanged(self, current, previous):
        if current.flags() & QtCore.Qt.ItemIsSelectable:
            self.subpage.emit(current.internalPointer())


class NavModel(QtCore.QAbstractItemModel):
    applets = ["OpenPGP", "YubiOath", "Yubico Bitcoin"]

    def __init__(self):
        super(NavModel, self).__init__()
        self.categories = {
            "Devices": self.createIndex(0, 0, "Devices"),
            "NEO Apps": self.createIndex(1, 0, "NEO Apps")
        }

        self.available_neos = AvailableNeos()
        self.neo_list = self.available_neos.neos
        self.available_neos.changed.connect(self.data_changed)

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
            return 2
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
