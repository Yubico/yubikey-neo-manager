from PySide import QtGui
from PySide import QtCore
from neoman.model.neo import YubiKeyNeo
from neoman.view.nav import NavTree
from neoman.view.welcome import WelcomePage
from neoman.view.neo import NeoPage
from neoman.storage import settings


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("YubiKey NEO Manager")
        self.setCentralWidget(self.build_ui())

        self.resize(settings.value('window/size', QtCore.QSize(400, 400)))
        pos = settings.value('window/pos')
        if pos:
            self.move(pos)

    def build_ui(self):
        widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.build_nav())
        layout.addWidget(self.build_main())

        self._nav.subpage.connect(self._main.setContent)
        self._main.setContent(self._nav.current)
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

    def closeEvent(self, event):
        settings.setValue('window/size', self.size())
        settings.setValue('window/pos', self.pos())
        event.accept()


class ContentWidget(QtGui.QStackedWidget):

    def __init__(self):
        super(ContentWidget, self).__init__()

        self._content = None

        self._start_page = WelcomePage()
        self.addWidget(self._start_page)

        self._neo_page = NeoPage()
        self.addWidget(self._neo_page)

        self._app_page = QtGui.QLabel("app")
        self.addWidget(self._app_page)

        self.setMinimumSize(400, 400)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

    @QtCore.Slot(object)
    def setContent(self, content):
        self._content = content

        if not content:
            self._neo_page.setNeo(None)
            self.setCurrentWidget(self._start_page)
        elif isinstance(content, YubiKeyNeo):
            self._neo_page.setNeo(content)
            self.setCurrentWidget(self._neo_page)
        else:
            self.setCurrentWidget(self._app_page)
