from PySide import QtCore
from neoman.model.device import NeoDevice


class NavModel(QtCore.QAbstractItemModel):
    devices = [NeoDevice("Dain's NEO", firmware="3.0.1"),
               NeoDevice("Klas's NEO")]
    applets = ["OpenPGP", "YubiOath", "Yubico Bitcoin"]

    def __init__(self):
        super(NavModel, self).__init__()
        self.categories = {
            "Devices": self.createIndex(0, 0, "Devices"),
            "NEO Apps": self.createIndex(1, 0, "NEO Apps")
        }

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            node = "Devices" if row == 0 else "NEO Apps"
            return self.categories[node]
        category = parent.internalPointer()
        if category == "Devices":
            return self.createIndex(row, column, self.devices[row])
        return self.createIndex(row, column, self.applets[row])

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        node = index.internalPointer()
        if node in self.categories:
            return QtCore.QModelIndex()
        if isinstance(node, NeoDevice):
            return self.categories['Devices']
        return self.categories['NEO Apps']

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return 2
        node = parent.internalPointer()
        if node in self.categories:
            return len(self.devices if node == "Devices" else self.applets)
        return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return str(index.internalPointer())

    def flags(self, index):
        node = index.internalPointer()
        if node in self.categories:
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
