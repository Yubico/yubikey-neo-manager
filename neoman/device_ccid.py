# Copyright (c) 2013 Yubico AB
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
from neoman.ykneomgr import *
from ctypes import POINTER, byref, c_size_t, create_string_buffer
from neoman.device import BaseDevice


assert ykneomgr_global_init(0) == 0


def check(status):
    if status != 0:
        raise Exception("Error: %d" % status)


class CCIDDevice(BaseDevice):

    def __init__(self, dev):
        self._dev = dev
        self._key = None
        self._locked = True
        self._serial = ykneomgr_get_serialno(dev)
        self._mode = ykneomgr_get_mode(dev)
        self._version = [
            ykneomgr_get_version_major(dev),
            ykneomgr_get_version_minor(dev),
            ykneomgr_get_version_build(dev)
        ]

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new_key):
        self._key = new_key

    @property
    def locked(self):
        return self._locked

    @property
    def mode(self):
        return self._mode

    @property
    def serial(self):
        return self._serial

    @property
    def version(self):
        return self._version

    def unlock(self):
        self._locked = True
        if not self._key:
            raise Exception("No transport key provided!")
        check(ykneomgr_authenticate(self._dev, self._key))
        self._locked = False

    def set_mode(self, mode):
        check(ykneomgr_modeswitch(self._dev, mode))
        self._mode = mode

    def list_apps(self):
        if self.locked:
            self.unlock()
        applist = create_string_buffer(1024)
        size = c_size_t()
        ykneomgr_applet_list(self._dev, applist, byref(size))
        apps = applist.raw[:size.value - 1].split('\0')

        return apps

    def close(self):
        if hasattr(self, '_dev'):
            ykneomgr_done(self._dev)
            del self._dev


def open_first_device():
    dev = POINTER(ykneomgr_dev)()
    check(ykneomgr_init(byref(dev)))
    try:
        check(ykneomgr_discover(dev))
    except Exception:
        ykneomgr_done(dev)
        raise

    return CCIDDevice(dev)
