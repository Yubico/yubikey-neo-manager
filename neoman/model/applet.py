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

from neoman.storage import capstore
from neoman import messages as m
import os


class Applet(object):

    def __init__(self, aid, name, description, latest_version="unknown",
                 cap_url=None, tabs=None):
        self.aid = aid
        self.name = name
        self.description = description
        self.latest_version = latest_version
        self.cap_url = cap_url
        self.tabs = tabs or {}

    def __str__(self):
        return self.name

    @property
    def is_downloaded(self):
        return capstore.has_file(self.aid, self.latest_version)

    @property
    def cap_file(self):
        return capstore.get_filename(self.aid, self.latest_version)


APPLETS = [
    #Applet("a0000005273001", "Manager", "YubiKey NEO Manager applet."),
    Applet("a0000005272001", "YubiKey OTP", "YubiKey OTP applet."),
    Applet("a0000005272101", "YubiOATH", "YubiOATH applet.", "0.2.1",
           "http://opensource.yubico.com/ykneo-oath/releases/ykneo-oath-0.2.1.cap"),
    Applet("a0000005272201", "U2F", "Yubico U2F applet.", "0.1.0"),
    #Applet("a0000005272102", "Yubico Bitcoin", "Yubico bitcoin applet."),
    Applet("d27600012401", "OpenPGP", "Open PGP applet.")
]

HIDDEN = [
    "a0000000035350",  # Security Domain
    "a000000527300101",  # Manager
    "d2760000850101"  # NDEF
]


def get_applets():
    return APPLETS


def get_applet(aid):
    if aid in HIDDEN:
        return None
    for applet in APPLETS:
        if aid.startswith(applet.aid):
            return applet
    return Applet(aid, m.unknown, m.unknown_applet)
