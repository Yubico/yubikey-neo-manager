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
from neoman.u2fh import *
from ctypes import (POINTER, byref, c_uint, c_size_t, c_ubyte,
                    create_string_buffer)
from neoman.device import BaseDevice
from neoman.exc import YkNeoMgrError
from neoman.model.modes import MODE
import os


def check(status):
    if status != 0:
        raise YkNeoMgrError(status)


if u2fh_global_init(1 if os.environ.has_key('NEOMAN_DEBUG') else 0) != 0:
    raise Exception("Unable to initialize ykneomgr")


libversion = u2fh_check_version(None)


devs = POINTER(u2fh_devs)()
check(u2fh_devs_init(byref(devs)))


U2F_VENDOR_FIRST = 0x40
TYPE_INIT = 0x80
U2FHID_PING = TYPE_INIT | 0x01
U2FHID_YUBIKEY_DEVICE_CONFIG = TYPE_INIT | U2F_VENDOR_FIRST


class U2FDevice(BaseDevice):

    def __init__(self, devs, index):
        self._devs = devs
        self._index = index
        self._serial = None
        self._version = (0, 0, 0)

    @property
    def u2f_capable(self):
        return True

    @property
    def mode(self):
        return MODE.mode_for_flags(False, False, True)

    @property
    def serial(self):
        return self._serial

    @property
    def version(self):
        return self._version

    def _sendrecv(self, cmd, data):
        buf_size = c_size_t(1024)
        #resp = (c_ubyte * buf_size.value)()
        resp = create_string_buffer(buf_size.value)

        check(u2fh_sendrecv(self._devs, self._index, cmd, data, len(data),
                            resp, byref(buf_size)))
        return resp.raw[0:buf_size.value]

    def set_mode(self, mode):
        data = ('%02x0f0000' % mode).decode('hex')
        self._sendrecv(U2FHID_YUBIKEY_DEVICE_CONFIG, data)

    def list_apps(self):
        return []

    def poll(self):
        return hasattr(self, '_index')

    def close(self):
        if hasattr(self, '_index'):
            del self._index
            del self._devs


def open_all_devices():
    max_index = c_uint()
    status = u2fh_devs_discover(devs, byref(max_index))
    if status == 0:
        # We have devices!
        devices = []
        resp = create_string_buffer(1024)
        for index in range(max_index.value + 1):
            buf_size = c_size_t(1024)
            if u2fh_get_device_description(
                devs, index, resp, byref(buf_size)) == 0:
                if resp.value.startswith('Yubikey NEO'):
                    devices.append(U2FDevice(devs, index))
        return devices
    else:
        # No devices!
        #u2fh_devs_done(devs)
        pass
    return []
