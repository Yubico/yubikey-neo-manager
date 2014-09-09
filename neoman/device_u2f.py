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
from ctypes import POINTER, byref, c_size_t, create_string_buffer
from neoman.device import BaseDevice
from neoman.exc import YkNeoMgrError
from neoman.model.modes import MODE
import os


if u2fh_global_init(1 if os.environ.has_key('NEOMAN_DEBUG') else 0) != 0:
    raise Exception("Unable to initialize ykneomgr")


U2F_VENDOR_FIRST = 0x40
TYPE_INIT = 0x80
U2FHID_PING = TYPE_INIT | 0x01
U2FHID_YUBIKEY_DEVICE_CONFIG = TYPE_INIT | U2F_VENDOR_FIRST


def check(status):
    if status != 0:
        raise YkNeoMgrError(status)


class U2FDevice(BaseDevice):

    def __init__(self, dev):
        self._dev = dev
        self._serial = None
        self._version = (3, 3, 0)

    @property
    def mode(self):
        return MODE.mode_for_flags(False, False, True)

    @property
    def serial(self):
        return self._serial

    @property
    def version(self):
        return self._version

    def set_mode(self, mode):
        data = ('%02x0f0000' % mode).decode('hex')
        buf_size = c_size_t(1024)
        resp = create_string_buffer(buf_size.value)

        check(u2fh_sendrecv(self._dev, U2FHID_YUBIKEY_DEVICE_CONFIG,
                            data, len(data), resp, byref(buf_size)))

    def list_apps(self):
        return []

    def poll(self):
        if not hasattr(self, '_dev'):
            return False

        buf_size = c_size_t(1024)
        resp = create_string_buffer(buf_size.value)
        if u2fh_sendrecv(self._dev, U2FHID_PING, '0', 1, resp,
                         byref(buf_size)) == 0:
            return True
        self.close()
        return False

    def close(self):
        if hasattr(self, '_dev'):
            del self._dev


def open_all_devices():
    devs = POINTER(u2fh_devs)()
    check(u2fh_devs_init(byref(devs)))
    status = u2fh_devs_discover(devs)
    if status == 0:
        # We have devices!
        num_devs = u2fh_num_devices(devs)
        devices = []
        for index in range(num_devs):
            dev = POINTER(u2fh_dev)()
            check(u2fh_get_device(devs, index, byref(dev)))
            devices.append(U2FDevice(dev))
        return devices
    else:
        # No devices!
        u2fh_devs_done(devs)
    return []
