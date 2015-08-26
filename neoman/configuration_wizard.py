from PySide import QtGui
from random import SystemRandom

from PySide.QtCore import QRegExp

from PySide.QtGui import QWizardPage, QVBoxLayout, QGroupBox, QRadioButton, \
    QLineEdit, QFormLayout, QWizard, QLabel, QPushButton

from neoman.legacy_otp import StaticPassword, open_otp


MODHEX_ALPHABET = 'cbdefghijklnrtuv'


class ConfigWizard(QtGui.QWizard):
    def __init__(self, slot, neo, parent=None):
        super(ConfigWizard, self).__init__(parent)
        self.slot = slot
        self.neo = neo
        self.addPage(FunctionPage(self))
        self.addPage(StaticPasswordPage(self))
        self.addPage(ResultsPage(slot, neo, self))
        self.setWindowTitle('Configuration')


class FunctionPage(QWizardPage):
    def __init__(self, parent=None):
        super(FunctionPage, self).__init__(parent)

        self.setTitle('Functionality')
        self.setSubTitle('The function to be invoked when long-pressing the YubiKey button.')

        groupBox = QGroupBox("Functionality")

        static = QRadioButton("&Static password")
        otp = QRadioButton("YubiKey &OTP")
        hotp = QRadioButton("OATH-&HOTP")

        static.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(static)
        vbox.addWidget(otp)
        vbox.addWidget(hotp)

        groupBox.setLayout(vbox)

        root = QVBoxLayout()
        root.addWidget(groupBox)
        self.setLayout(root)


class StaticPasswordPage(QWizardPage):
    def __init__(self, parent=None):
        super(StaticPasswordPage, self).__init__(parent)

        self.setTitle('Static Password')
        self.setSubTitle('The password that the YubiKey should emit. Only characters from the modhex alphabet (c, b, d, e, f, g, h, i, j, k, l, n, r, t, u, v) may be used.')
        self.setCommitPage(True)
        self.setButtonText(QWizard.CommitButton, 'Write config')

        self.password_field = QLineEdit()
        self.password_field.setMaxLength(38)
        self.password_field.setValidator(ModhexValidator())

        self.scancodes = QLineEdit()
        self.scancodes.setReadOnly(True)

        form = QFormLayout()
        form.addRow(self.tr('&Password:'), self.password_field)

        randomize = QPushButton('Randomize')
        randomize.clicked.connect(self.randomize_password)

        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(randomize)

        self.setLayout(vbox)

        self.registerField('static_password', self.password_field)

    def randomize_password(self):
        random = SystemRandom()
        password = ''.join([MODHEX_ALPHABET[random.randrange(16)] for i in xrange(38)])
        self.password_field.setText(password)


class ModhexValidator(QtGui.QRegExpValidator):
    def __init__(self, parent=None):
        rx = QRegExp('[c|b|d|e|f|g|h|i|j|k|l|n|r|t|u|v]*')
        super(ModhexValidator, self).__init__(rx, parent)


class ResultsPage(QWizardPage):
    def __init__(self, slot, neo, parent=None):
        super(ResultsPage, self).__init__(parent)
        self.slot = slot
        self.neo = neo

    def initializePage(self):
        self.setTitle('Results')
        self.label = QLabel()

        self.neo._mutex.lock()
        try:
            static_pass = StaticPassword(open_otp())
            static_pass.put(self.slot, self.field('static_password'), True)
            self.label.setText('Successfully wrote configuration!')
        except Exception as e:
            self.label.setText('Error when writing configuration: ' + e.message)
        self.neo._mutex.unlock()

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.label)
        self.setLayout(vbox)
