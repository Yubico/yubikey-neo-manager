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
MODE_HID = 0
MODE_CCID = 1
MODE_HID_CCID = 2


class BaseDevice(object):

    @property
    def mode(self):
        raise NotImplementedError()

    @property
    def has_ccid(self):
        return self.mode & 0x0f in [MODE_CCID, MODE_HID_CCID]

    @property
    def serial(self):
        raise NotImplementedError()

    @property
    def version(self):
        raise NotImplementedError()

    def __del__(self):
        if hasattr(self, 'close'):
            self.close()

    def __str__(self):
        return "NEO[mode=%x, serial=%s]" % (self.mode, self.serial)


def open_first_device():
    for _ in range(3):  # Retry a few times as this sometimes fails.
        try:
            from neoman.device_ccid import open_first_device as open_ccid
            return open_ccid()
        except Exception:
            pass
    try:
        from neoman.device_hid import open_first_device as open_hid
        return open_hid()
    except Exception as e:
        return None


def open_all_devices(existing=None):
    devices = []
    has_composite = False
    try:
        from neoman.device_ccid import open_all_devices as open_ccid_all
        for dev in open_ccid_all(existing):
            has_composite = has_composite or dev.mode & 0xf == MODE_HID_CCID
            devices.append(dev)
    except Exception:
        pass
    try:
        from neoman.device_hid import open_first_device as open_hid
        # Close any exisitng HID devices as we are going to reopen them.
        for dev in existing:
            if not dev.has_ccid:
                dev.close()
        dev = open_hid()
        # Avoid adding any HID devices which do not expose a serial if we know
        # there are composite devices (as to not add them twice).
        if not dev.serial and has_composite:
            dev.close()
        else:
            devices.append(dev)
    except Exception:
        pass
    return devices
