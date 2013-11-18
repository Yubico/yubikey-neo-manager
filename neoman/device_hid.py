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
from neoman.ykpers import *
from ctypes import byref, c_uint
from neoman.device import BaseDevice, MODE_HID

if not yk_init():
    raise Exception("Unable to initialize ykpers")


class HIDDevice(BaseDevice):

    def __init__(self, dev):
        self._dev = dev

        ser = c_uint()
        if yk_get_serial(dev, 0, 0, byref(ser)):
            self._serial = ser.value
        else:
            self._serial = None

        status = ykds_alloc()
        try:
            if yk_get_status(dev, status):
                self._version = [
                    ykds_version_major(status),
                    ykds_version_minor(status),
                    ykds_version_build(status)
                ]
            else:
                self._version = [0, 0, 0]
        finally:
            ykds_free(status)

    @property
    def mode(self):
        return MODE_HID

    @property
    def serial(self):
        return self._serial

    @property
    def version(self):
        return self._version

    def set_mode(self, mode):
        if self.version[0] < 3:
            raise Exception("Mode Switching requires version >= 3")

        config = ykp_alloc_device_config()
        ykp_set_device_mode(config, mode)
        if not yk_write_device_config(self._dev, config):
            raise Exception("Failed writing device config!")
        ykp_free_device_config(config)

    def close(self):
        if hasattr(self, '_dev'):
            yk_close_key(self._dev)
            del self._dev


def open_first_device():
    dev = yk_open_first_key()
    if not dev:
        raise Exception("Unable to open YubiKey NEO!")

    hid_device = HIDDevice(dev)
    if hid_device.version[0] < 3:
        raise Exception("Device is not a YubiKey NEO!")

    return hid_device
