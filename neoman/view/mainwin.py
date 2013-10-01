from PySide import QtGui
from PySide import QtCore
from neoman.model.nav import NavModel
from neoman.model.device import NeoDevice
from neoman.view.device import QDevice


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("YubiKey NEO Manager")
        self.setCentralWidget(self.build_ui())

    @QtCore.Slot(object)
    def open_page(self, target):
        self._main.currentWidget().deleteLater()

        if isinstance(target, NeoDevice):
            widget = QDevice(target)
        else:
            widget = QtGui.QLabel(str(target))

        self._main.addWidget(widget)

    def build_ui(self):
        widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.build_nav())
        layout.addWidget(self.build_main())
        widget.setLayout(layout)

        return widget

    def build_nav(self):
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._nav = NavTree()
        self._nav.subpage.connect(self.open_page)
        layout.addWidget(self._nav)

        widget = QtGui.QWidget()
        widget.setLayout(layout)

        widget.setMaximumWidth(200)
        widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                             QtGui.QSizePolicy.Expanding)
        return widget

    def build_main(self):
        self._main = QtGui.QStackedWidget()
        self._main.addWidget(QtGui.QLabel("Hello world"))
        self._main.setMinimumSize(400, 400)
        self._main.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                 QtGui.QSizePolicy.Expanding)
        return self._main


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
