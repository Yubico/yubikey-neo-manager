import sys
from PySide import QtGui, QtCore
from neoman.view.main import MainWindow

QtCore.QCoreApplication.setOrganizationName('Yubico')
QtCore.QCoreApplication.setOrganizationDomain('yubico.com')
QtCore.QCoreApplication.setApplicationName('YubiKey NEO Manager')


def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
