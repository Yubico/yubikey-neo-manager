from PySide import QtGui, QtCore
from neoman.model.applet import Applet


class AppletPage(QtGui.QTabWidget):
    applet = QtCore.Signal(Applet)

    def __init__(self):
        super(AppletPage, self).__init__()
        self._applet = None

        overview = OverviewTab()
        self.applet.connect(overview.set_applet)
        self.addTab(overview, "Overview")

    def setApplet(self, applet):
        self._applet = applet
        self.applet.emit(applet)


class OverviewTab(QtGui.QWidget):

    def __init__(self):
        super(OverviewTab, self).__init__()
        self._applet = None
        self._name = QtGui.QLabel()
        self._aid = QtGui.QLabel()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._name)
        layout.addWidget(self._aid)
        layout.addStretch()

        self.setLayout(layout)

    @QtCore.Slot(Applet)
    def set_applet(self, applet):
        self._applet = applet
        self._name.setText("Name: %s" % applet.name)
        self._aid.setText("AID: %s" % applet.aid)
