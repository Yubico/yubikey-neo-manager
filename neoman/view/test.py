from neoman.ykpers import *
from ctypes import c_uint, byref

from PySide.QtCore import QObject, Signal, Property, QUrl
from PySide.QtDeclarative import QDeclarativeView
import sys
import os

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(__file__)

__all__ = ['TestWindow']


class YubiKey(QObject):

    def __init__(self):
        super(YubiKey, self).__init__()

        yk_init()
        yk = yk_open_first_key()

        if yk:
            ser = c_uint()
            yk_get_serial(yk, 1, 0, byref(ser))
            self.serial = ser.value

            status = ykds_alloc()
            yk_get_status(yk, status)

            self.version = "%d.%d.%d" % (ykds_version_major(status),
                                         ykds_version_minor(status),
                                         ykds_version_build(status))
            yk_close_key(yk)
            self.__message = "Serial: %d, version: %s" % (self.serial,
                                                          self.version)
        else:
            self.__message = "No key found!"
        yk_release()
        self.changed.emit()

    def get_message(self):
        return self.__message

    changed = Signal()

    message = Property(str, get_message, None, notify=changed)


class TestWindow(QDeclarativeView):

    def __init__(self, parent=None):
        super(TestWindow, self).__init__(parent)

        self.setWindowTitle('YubiKey NEO Manager')

        ctx = self.rootContext()
        ctx.setContextProperty('yubikey', YubiKey())

        url = QUrl(os.path.join(basedir, 'test.qml'))
        self.setSource(url)
        self.setResizeMode(QDeclarativeView.SizeRootObjectToView)
