from PySide import QtGui, QtCore
from neoman.model.neo import AvailableNeos, YubiKeyNeo
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
        else:
            self.current = None
            self.subpage.emit(None)

    def _data_changed(self):
        if not self.current and self.model().neo_list:
            self.setCurrentIndex(
                self.model().index(0, 0, self.model().categories['Devices']))


class NavModel(QtCore.QAbstractItemModel):

    def __init__(self):
        super(NavModel, self).__init__()
        self.categories = {
            "Devices": self.createIndex(0, 0, "Devices"),
            "NEO Apps": self.createIndex(1, 0, "NEO Apps")
        }

        self.applets = APPLETS
        self.available_neos = AvailableNeos()
        self.neo_list = []
        self.available_neos.changed.connect(self.data_changed)
        self.available_neos.start()
        QtCore.QCoreApplication.instance().aboutToQuit.connect(
            self.available_neos.stop)

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
