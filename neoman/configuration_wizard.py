from PySide import QtGui
from random import SystemRandom

from PySide.QtCore import QRegExp

from PySide.QtGui import QWizardPage, QVBoxLayout, QGroupBox, QRadioButton, \
    QLineEdit, QFormLayout, QWizard, QLabel, QPushButton

from neoman.legacy_otp import StaticPassword, open_otp, ChallengeResponse


MODHEX_ALPHABET = 'cbdefghijklnrtuv'
HEX_ALPHABET = '0123456789ABCDEF'


class ConfigWizard(QtGui.QWizard):

    Page_Function = 1
    Page_StaticPassword = 2
    Page_ChallengeResponse = 3
    Page_Results = 4

    def __init__(self, slot, neo, parent=None):
        super(ConfigWizard, self).__init__(parent)
        self.slot = slot
        self.neo = neo
        self.setWindowTitle('Slot Configuration')

        self.setPage(ConfigWizard.Page_Function, FunctionPage(slot, self))
        self.setPage(ConfigWizard.Page_StaticPassword, StaticPasswordPage(self))
        self.setPage(ConfigWizard.Page_ChallengeResponse, ChallengeResponsePage(self))
        self.setPage(ConfigWizard.Page_Results, ResultsPage(slot, neo, self))


class FunctionPage(QWizardPage):
    def __init__(self, slot, parent=None):
        super(FunctionPage, self).__init__(parent)

        self.setTitle('Functionality')
        self.setSubTitle('The function to be configured for slot %s.' % slot)

        groupBox = QGroupBox("Functionality")

        self.static = QRadioButton("&Static password")
        self.challenge = QRadioButton("&Challenge-response")

        self.registerField('staticpass_radio', self.static)
        self.registerField('challengeresponse_radio', self.challenge)

        self.static.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(self.static)
        vbox.addWidget(self.challenge)

        groupBox.setLayout(vbox)

        root = QVBoxLayout()
        root.addWidget(groupBox)
        self.setLayout(root)

    def nextId(self):
        if self.static.isChecked():
            return ConfigWizard.Page_StaticPassword
        if self.challenge.isChecked():
            return ConfigWizard.Page_ChallengeResponse


class StaticPasswordPage(QWizardPage):
    def __init__(self, parent=None):
        super(StaticPasswordPage, self).__init__(parent)

        self.setTitle('Static Password')
        self.setSubTitle('The password that the YubiKey should emit. Only characters from the modhex alphabet (c, b, d, e, f, g, h, i, j, k, l, n, r, t, u, v) may be used.')
        self.setCommitPage(True)
        self.setButtonText(QWizard.CommitButton, '&Write config')

        self.password_field = QLineEdit()
        self.password_field.setMaxLength(38)
        self.password_field.setValidator(ModhexValidator())

        form = QFormLayout()
        form.addRow(self.tr('&Password:'), self.password_field)

        randomize = QPushButton('&Randomize')
        randomize.clicked.connect(self.randomize_password)

        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(randomize)

        self.setLayout(vbox)

        self.registerField('static_password', self.password_field)

    def randomize_password(self):
        random = SystemRandom()
        password = ''.join([MODHEX_ALPHABET[random.randrange(len(MODHEX_ALPHABET))] for i in xrange(38)])
        self.password_field.setText(password)

    def nextId(self):
        return ConfigWizard.Page_Results


class ModhexValidator(QtGui.QRegExpValidator):
    def __init__(self, parent=None):
        rx = QRegExp('[c|b|d|e|f|g|h|i|j|k|l|n|r|t|u|v]*')
        super(ModhexValidator, self).__init__(rx, parent)


class ChallengeResponsePage(QWizardPage):
    def __init__(self, parent=None):
        super(ChallengeResponsePage, self).__init__(parent)

        self.setTitle('Challenge-response')
        self.setSubTitle('When given a challenge, the YubiKey will perform a HMAC-SHA1 operation using the configured secret and return the result.')
        self.setCommitPage(True)
        self.setButtonText(QWizard.CommitButton, '&Write config')

        self.secret_field = QLineEdit()
        self.secret_field.setValidator(HexValidator())
        self.secret_field.setInputMask('HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH HH')
        self.secret_field.setText('0' * 40)

        form = QFormLayout()
        form.addRow(self.tr('&Secret (hexadecimal):'), self.secret_field)

        randomize = QPushButton('&Randomize')
        randomize.clicked.connect(self.randomize_password)

        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(randomize)

        self.setLayout(vbox)

        self.registerField('challenge_secret', self.secret_field)

    def randomize_password(self):
        random = SystemRandom()
        password = ''.join([HEX_ALPHABET[random.randrange(len(HEX_ALPHABET))] for i in xrange(40)])
        self.secret_field.setText(password)

    def nextId(self):
        return ConfigWizard.Page_Results


class HexValidator(QtGui.QRegExpValidator):
    def __init__(self, parent=None):
        rx = QRegExp('[\d|a-f|A-F]*')
        super(HexValidator, self).__init__(rx, parent)


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
            if self.field('staticpass_radio'):
                static_pass = StaticPassword(open_otp())
                static_pass.put(self.slot, self.field('static_password'), True)
            elif self.field('challengeresponse_radio'):
                secret = self.field('challenge_secret')
                print secret.replace(' ', '').lower()
                chal_resp = ChallengeResponse(open_otp())
                chal_resp.put(self.slot, secret.replace(' ', '').lower())
            self.label.setText('Successfully wrote configuration!')
        except Exception as e:
            self.label.setText('Error when writing configuration: ' + e.message)
        self.neo._mutex.unlock()

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.label)
        self.setLayout(vbox)
