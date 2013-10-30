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


class Applet(object):

    def __init__(self, aid, name, description, latest_version="unknown",
                 cap_file=None, tabs=None):
        self.aid = aid
        self.name = name
        self.description = description
        self.latest_version = latest_version
        self.cap_file = cap_file
        self.tabs = tabs if tabs else {}

    def __str__(self):
        return self.name


APPLETS = [
    Applet("a0000005272001", "YubiKey", "YubiKey OTP applet."),
    Applet("a0000005272101", "YubiOATH", "YubiOATH applet."),
    #Applet("a0000005272102", "Yubico Bitcoin", "Yubico bitcoin applet."),
    Applet("d27600012401", "OpenPGP", "Open PGP applet.")
]

HIDDEN = [
    "a0000000035350"  # Security Domain
]


def get_applets():
    return APPLETS


def get_applet(aid):
    if aid in HIDDEN:
        return None
    for applet in APPLETS:
        if applet.aid == aid:
            return applet
    return Applet(aid, "Unknown", "Unknown applet")
