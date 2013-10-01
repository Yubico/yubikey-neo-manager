from PySide import QtGui
from PySide import QtCore
from neoman.model.nav import NavModel
from neoman.model.device import NeoDevice
from neoman.view.device import DeviceWidget


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("YubiKey NEO Manager")
        self.setCentralWidget(self.build_ui())

    def build_ui(self):
        widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.build_nav())
        layout.addWidget(self.build_main())

        self._nav.subpage.connect(self._main.setContent)
        widget.setLayout(layout)

        return widget

    def build_nav(self):
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._nav = NavTree()
        layout.addWidget(self._nav)

        widget = QtGui.QWidget()
        widget.setLayout(layout)

        widget.setMaximumWidth(200)
        widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                             QtGui.QSizePolicy.Expanding)
        return widget

    def build_main(self):
        self._main = ContentWidget()
        return self._main


class ContentWidget(QtGui.QStackedWidget):

    def __init__(self):
        super(ContentWidget, self).__init__()

        self._content = None

        self.addWidget(QtGui.QLabel("HelloWorld"))

        self._device_page = DeviceWidget()
        self.addWidget(self._device_page)

        self._app_page = QtGui.QLabel("app")
        self.addWidget(self._app_page)

        self.setMinimumSize(400, 400)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

    def setContent(self, content):
        self._content = content

        if isinstance(content, NeoDevice):
            self._device_page.device = content
            self.setCurrentWidget(self._device_page)
        else:
            self.setCurrentWidget(self._app_page)

    def getContent(self):
        return self._content

    content = QtCore.Property(object, getContent, setContent)


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
