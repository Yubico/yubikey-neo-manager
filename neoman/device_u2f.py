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
from ctypes import POINTER, byref, c_uint, c_size_t, create_string_buffer
from neoman.device import BaseDevice
from neoman.exc import YkNeoMgrError, ModeSwitchError
from neoman.model.modes import MODE
from neoman.yk4_utils import (parse_tlv_list, YK4_CAPA_TAG, YK4_CAPA1_OTP,
                              YK4_CAPA1_CCID, YK4_CAPA1_U2F)
import os


def check(status):
    if status != 0:
        raise YkNeoMgrError(status)


if u2fh_global_init(1 if 'NEOMAN_DEBUG' in os.environ else 0) != 0:
    raise Exception("Unable to initialize ykneomgr")


libversion = u2fh_check_version(None)


devs = POINTER(u2fh_devs)()
check(u2fh_devs_init(byref(devs)))


U2F_VENDOR_FIRST = 0x40
TYPE_INIT = 0x80
U2FHID_PING = TYPE_INIT | 0x01
U2FHID_YUBIKEY_DEVICE_CONFIG = TYPE_INIT | U2F_VENDOR_FIRST
U2FHID_YK4_CAPABILITIES = TYPE_INIT | U2F_VENDOR_FIRST + 2


class U2FDevice(BaseDevice):
    device_type = 'U2F'
    version = (0, 0, 0)
    allowed_modes = (True, True, True)

    def __init__(self, devs, index,
                 mode=MODE.mode_for_flags(False, False, True)):
        self._devs = devs
        self._index = index
        self._mode = mode
        self._serial = None

    @property
    def mode(self):
        return self._mode

    @property
    def serial(self):
        return self._serial

    def _sendrecv(self, cmd, data):
        buf_size = c_size_t(1024)
        resp = create_string_buffer(buf_size.value)

        check(u2fh_sendrecv(self._devs, self._index, cmd, data, len(data),
                            resp, byref(buf_size)))
        return resp.raw[0:buf_size.value]

    def set_mode(self, mode):
        data = ('%02x0f0000' % mode).decode('hex')
        try:
            self._sendrecv(U2FHID_YUBIKEY_DEVICE_CONFIG, data)
            self._mode = mode
        except YkNeoMgrError:
            raise ModeSwitchError()

    def list_apps(self):
        return []

    def poll(self):
        return hasattr(self, '_index')

    def close(self):
        if hasattr(self, '_index'):
            del self._index
            del self._devs


class SKYDevice(U2FDevice):
    supported = False
    default_name = 'Security Key by Yubico'


class YK4Device(U2FDevice):
    default_name = 'YubiKey 4'

    def __init__(self, devs, index, mode):
        super(YK4Device, self).__init__(devs, index, mode)
        self._read_capabilities()

        if self._cap == 0x07:  # YK Edge should not allow CCID.
            self.default_name = 'YubiKey Edge'
            self.allowed_modes = (True, False, True)

    def _read_capabilities(self):
        data = '\0'
        resp = self._sendrecv(U2FHID_YK4_CAPABILITIES, data)
        self._cap_data = parse_tlv_list(resp[1:ord(resp[0]) + 1])
        self._cap = int(self._cap_data.get(YK4_CAPA_TAG, '0').encode('hex'), 16)
        self.allowed_modes = (
            bool(self._cap & YK4_CAPA1_OTP),
            bool(self._cap & YK4_CAPA1_CCID),
            bool(self._cap & YK4_CAPA1_U2F)
        )


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
                    mode = MODE.mode_for_flags(
                        'OTP' in resp.value,
                        'CCID' in resp.value,
                        'U2F' in resp.value
                    )
                    devices.append(U2FDevice(devs, index, mode))
                elif resp.value.startswith('Yubikey 4'):
                    mode = MODE.mode_for_flags(
                        'OTP' in resp.value,
                        'CCID' in resp.value,
                        'U2F' in resp.value
                    )
                    devices.append(YK4Device(devs, index, mode))
                elif resp.value.startswith('Security Key by Yubico'):
                    devices.append(SKYDevice(devs, index))
        return devices
    else:
        # No devices!
        # u2fh_devs_done(devs)
        pass
    return []
