import os
from PySide import QtCore

__all__ = [
    'CONFIG_HOME',
    'settings'
]

CONFIG_HOME = os.path.join(os.path.expanduser('~'), '.neoman')

settings = QtCore.QSettings(os.path.join(CONFIG_HOME, 'settings.ini'),
                            QtCore.QSettings.IniFormat)
