from PySide import QtGui


class WelcomePage(QtGui.QLabel):

    def __init__(self):
        super(WelcomePage, self).__init__()

        self.setText("YubiKey NEO Manager")
