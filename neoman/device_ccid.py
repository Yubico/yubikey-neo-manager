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
from neoman.exc import YkNeoMgrError, ModeSwitchError
from neoman.yk4_utils import (parse_tlv_list, YK4_CAPA_TAG, YK4_CAPA1_OTP,
                              YK4_CAPA1_CCID, YK4_CAPA1_U2F)
import os


if ykneomgr_global_init(1 if 'NEOMAN_DEBUG' in os.environ else 0) != 0:
    raise Exception("Unable to initialize ykneomgr")


libversion = ykneomgr_check_version(None)


U2F_SELECT_1 = '00a4040008a0000006472f0001'.decode('hex')
U2F_SELECT_2 = '00a4040007a0000005271002'.decode('hex')

YK4_SELECT_MGMT = '00a4040008a000000527471117'.decode('hex')
YK4_GET_CAPA = '001d0000'.decode('hex')


class CCIDDevice(BaseDevice):
    device_type = 'CCID'
    version = (0, 0, 0)

    def __init__(self, dev, version=None, dev_str=None):
        self._dev = dev
        self._dev_str = dev_str
        self._key = None
        self._locked = True
        self._serial = ykneomgr_get_serialno(dev) or None
        self._mode = ykneomgr_get_mode(dev)
        self._version = (
            ykneomgr_get_version_major(dev),
            ykneomgr_get_version_minor(dev),
            ykneomgr_get_version_build(dev)
        )
        self._supports_u2f = self._has_u2f_applet()
        self._apps = None
        self._broken = False

    def _has_u2f_applet(self):
        return '\x90\x00' in [self.send_apdu(U2F_SELECT_1)[-2:],
                              self.send_apdu(U2F_SELECT_2)[-2:]]

    def check(self, status):
        if status != 0:
            self._broken = True
            raise YkNeoMgrError(status)

    @property
    def allowed_modes(self):
        return (True, True, self._supports_u2f)

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

    def unlock(self):
        self._locked = True
        if not self._key:
            raise ValueError("No transport key provided!")
        self.check(ykneomgr_authenticate(self._dev, self._key))
        self._locked = False

    def set_mode(self, mode):
        if ykneomgr_modeswitch(self._dev, mode) != 0:
            raise ModeSwitchError()
        self._mode = mode

    def send_apdu(self, apdu):
        self._locked = True
        buf_size = c_size_t(1024)
        resp = create_string_buffer(buf_size.value)
        self.check(ykneomgr_send_apdu(self._dev, apdu, len(apdu), resp,
                                      byref(buf_size)))
        return resp.raw[0:buf_size.value]

    # Deprecated, DO NOT USE!
    def _list_apps(self, refresh=False):
        if refresh or self._apps is None:
            if self.locked:
                self.unlock()
            size = c_size_t()
            self.check(ykneomgr_applet_list(self._dev, None, byref(size)))
            applist = create_string_buffer(size.value)
            self.check(ykneomgr_applet_list(self._dev, applist, byref(size)))
            self._apps = applist.raw.strip('\0').split('\0')

        return self._apps

    def delete_app(self, aid):
        if self.locked:
            self.unlock()
        aid_bytes = aid.decode('hex')
        self.check(ykneomgr_applet_delete(self._dev, aid_bytes,
                                          len(aid_bytes)))

    def install_app(self, path):
        if self.locked:
            self.unlock()
        self.check(ykneomgr_applet_install(self._dev,
                                           create_string_buffer(path)))

    def close(self):
        if hasattr(self, '_dev'):
            ykneomgr_done(self._dev)
            del self._dev


class YK4Device(CCIDDevice):
    default_name = 'YubiKey 4'
    allowed_modes = (False, False, False)

    def __init__(self, dev, version, dev_str):
        super(YK4Device, self).__init__(dev, version, dev_str)
        self._read_capabilities()

        if self._cap == 0x07:  # YK Edge should not allow CCID.
            self.default_name = 'YubiKey Edge'
            self.allowed_modes = (True, False, True)

    def _read_capabilities(self):
        self.send_apdu(YK4_SELECT_MGMT)
        resp = self.send_apdu(YK4_GET_CAPA)
        resp, status = resp[:-2], resp[-2:]
        if status != '\x90\x00':
            resp = '\x00'
        if self.version == (4, 2, 4):  # 4.2.4 has a bug with capabilities.
            resp = '0301013f'.decode('hex')
        self._cap_data = parse_tlv_list(resp[1:ord(resp[0]) + 1])
        self._cap = int(self._cap_data.get(YK4_CAPA_TAG, '0').encode('hex'), 16)
        self.allowed_modes = (
            bool(self._cap & YK4_CAPA1_OTP),
            bool(self._cap & YK4_CAPA1_CCID),
            bool(self._cap & YK4_CAPA1_U2F)
        )

    @property
    def version(self):
        return self._version


def check(status):
    if status != 0:
        raise YkNeoMgrError(status)


def create_device(dev, dev_str=None):
    version = (
        ykneomgr_get_version_major(dev),
        ykneomgr_get_version_minor(dev),
        ykneomgr_get_version_build(dev)
    )
    if version[0] == 4:
        return YK4Device(dev, version, dev_str)
    return CCIDDevice(dev, version, dev_str)


def open_first_device():
    dev = POINTER(ykneomgr_dev)()
    check(ykneomgr_init(byref(dev)))
    try:
        check(ykneomgr_discover(dev))
    except Exception:
        ykneomgr_done(dev)
        raise

    return create_device(dev)


def open_all_devices(existing=None):
    dev = POINTER(ykneomgr_dev)()
    check(ykneomgr_init(byref(dev)))
    size = c_size_t()
    check(ykneomgr_list_devices(dev, None, byref(size)))
    devlist = create_string_buffer(size.value)
    check(ykneomgr_list_devices(dev, devlist, byref(size)))
    names = devlist.raw.strip('\0').split('\0')
    devices = []
    for d in existing or []:
        if getattr(d, '_dev_str', None) in names:
            if d._broken:
                d.close()
            else:
                devices.append(d)
                names.remove(d._dev_str)
    for name in names:
        if not dev:
            dev = POINTER(ykneomgr_dev)()
            check(ykneomgr_init(byref(dev)))
        if ykneomgr_connect(dev, create_string_buffer(name)) == 0:
            devices.append(create_device(dev, name))
            dev = None
    if dev:
        ykneomgr_done(dev)
    return devices
