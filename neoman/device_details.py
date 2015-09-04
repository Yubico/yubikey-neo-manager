from PySide.QtGui import QDialog, QGridLayout, QLabel


class DeviceDetailsDialog(QDialog):

    def __init__(self, neo, parent=None):
        super(DeviceDetailsDialog, self).__init__(parent)
        self.setWindowTitle('Device details')

        grid = QGridLayout()

        grid.addWidget(QLabel('Firmware version:'), 0, 0)
        grid.addWidget(QLabel('.'.join(map(str, neo.version))), 0, 1)
        grid.addWidget(QLabel('Serial number:'), 1, 0)
        grid.addWidget(QLabel(str(neo._serial)), 1, 1)

        self.setLayout(grid)