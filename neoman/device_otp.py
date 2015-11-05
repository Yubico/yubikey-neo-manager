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
from ctypes import byref, c_uint, c_int, c_size_t, create_string_buffer
from neoman.exc import ModeSwitchError
from neoman.device import BaseDevice
from neoman.model.modes import MODE
from neoman.yk4_utils import (parse_tlv_list, YK4_CAPA_TAG, YK4_CAPA1_OTP,
                              YK4_CAPA1_CCID, YK4_CAPA1_U2F)

if not yk_init():
    raise Exception("Unable to initialize ykpers")


libversion = ykpers_check_version(None)


def read_version(dev):
    status = ykds_alloc()
    try:
        if yk_get_status(dev, status):
            return (
                ykds_version_major(status),
                ykds_version_minor(status),
                ykds_version_build(status)
            )
        else:
            return (0, 0, 0)
    finally:
        ykds_free(status)


class OTPDevice(BaseDevice):
    device_type = 'OTP'
    allowed_modes = (True, False, False)

    def __init__(self, dev, version):
        self._dev = dev
        self._version = version

        ser = c_uint()
        if yk_get_serial(dev, 0, 0, byref(ser)):
            self._serial = ser.value
        else:
            self._serial = None

        self._mode = self._read_mode(dev)
        self.allowed_modes = (True, True, version >= (3, 3, 0))

    def _read_mode(self, dev):
        vid = c_int()
        pid = c_int()
        try:
            yk_get_key_vid_pid(dev, byref(vid), byref(pid))
            mode = 0x0f & pid.value
            if mode == 1:  # mode 1 has PID 0112 and mode 2 has PID 0111
                return 2
            elif mode == 2:
                return 1
            else:  # all others have 011x where x = mode
                return mode
        except:  # We know we at least have OTP enabled...
            return MODE.mode_for_flags(True, False, False)

    @property
    def mode(self):
        return self._mode

    @property
    def serial(self):
        return self._serial

    @property
    def version(self):
        return self._version

    def set_mode(self, mode):
        if self.version[0] < 3:
            raise ValueError("Mode Switching requires version >= 3")

        config = ykp_alloc_device_config()
        ykp_set_device_mode(config, mode)
        try:
            if not yk_write_device_config(self._dev, config):
                raise ModeSwitchError()
        finally:
            ykp_free_device_config(config)
        self._mode = mode

    def list_apps(self):
        return []

    def close(self):
        if hasattr(self, '_dev'):
            yk_close_key(self._dev)
            del self._dev


class YKStandardDevice(BaseDevice):
    device_type = 'OTP'
    supported = False
    serial = None
    version = (0, 0, 0)
    mode = MODE.mode_for_flags(True, False, False)

    def __init__(self, dev, version):
        self._dev = dev
        self._version = version

    @property
    def default_name(self):
        return 'YubiKey %s' % '.'.join(map(str, self._version))

    def close(self):
        if hasattr(self, '_dev'):
            yk_close_key(self._dev)
            del self._dev


class YKPlusDevice(YKStandardDevice):
    mode = MODE.mode_for_flags(True, False, True)
    default_name = 'YubiKey Plus'


class YK4Device(OTPDevice):
    default_name = 'YubiKey 4'

    def __init__(self, dev, version):
        super(YK4Device, self).__init__(dev, version)
        self._read_capabilities()

        if self._cap == 0x07:  # YK Edge should not allow CCID.
            self.default_name = 'YubiKey Edge'
            self.allowed_modes = (True, False, True)

    def _read_mode(self, dev):
        vid = c_int()
        pid = c_int()
        try:
            yk_get_key_vid_pid(dev, byref(vid), byref(pid))
            mode = 0x0f & pid.value
            return MODE.mode_for_flags(bool(mode & 1), bool(mode & 4),
                                       bool(mode & 2))
        except:  # We know we at least have OTP enabled...
            return MODE.mode_for_flags(True, False, False)

    def _read_capabilities(self):
        buf_size = c_size_t(1024)
        resp = create_string_buffer(buf_size.value)
        yk_get_capabilities(self._dev, 0, 0, resp, byref(buf_size))
        resp = resp.raw
        self._cap_data = parse_tlv_list(resp[1:ord(resp[0]) + 1])
        self._cap = int(self._cap_data.get(YK4_CAPA_TAG, '0').encode('hex'), 16)
        self.allowed_modes = (
            bool(self._cap & YK4_CAPA1_OTP),
            bool(self._cap & YK4_CAPA1_CCID),
            bool(self._cap & YK4_CAPA1_U2F)
        )


def open_first_device():
    dev = yk_open_first_key()
    if not dev:
        raise Exception("Unable to open YubiKey NEO!")

    version = read_version(dev)

    if version >= (4, 1, 0):
        return YK4Device(dev, version)
    elif version >= (4, 0, 0):
        return YKPlusDevice(dev, version)
    elif version >= (3, 0, 0):
        return OTPDevice(dev, version)
    else:
        return YKStandardDevice(dev, version)
