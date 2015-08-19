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

from PySide import QtCore, QtNetwork
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from neoman.model.jsapi import JS_API, AppletNotInstalledException
from neoman.networker import NetWorker
from neoman.storage import CONFIG_HOME, capstore
from neoman import messages as m
import os
import json


__all__ = ['Applet', 'AppletManager']


DB_FILE = os.path.join(CONFIG_HOME, "appletdb.json")


class Applet(object):

    def __init__(self, aid, name, description, **kwargs):
        self.aid = aid
        self.name = name
        self.description = description
        self.latest_version = kwargs.get('version', 'unknown')
        self.cap_url = kwargs.get('cap_url', None)
        self.cap_sha1 = kwargs.get('cap_sha1', None)
        self.allow_uninstall = kwargs.get('allow_uninstall', True)
        self._js_version = kwargs.get('js_version', None)
        self.tabs = kwargs.get('tabs', {})

    def __str__(self):
        return self.name

    @property
    def is_downloaded(self):
        return capstore.has_file(self.aid, self.latest_version)

    @property
    def cap_file(self):
        return capstore.get_filename(self.aid, self.latest_version,
                                     self.cap_sha1)

    def get_status(self, neo):
        installed = False
        version = None
        try:
            with JS_API(neo, self) as api:
                installed = True
                if self._js_version:
                    version = api.run(self._js_version)
        except AppletNotInstalledException:
            pass
        return (installed, version)


class AppletManager(object):

    def __init__(self):
        self._hidden = []
        self._applets = []
        self._read_db()
        self.networker = NetWorker(QtCore.QCoreApplication.instance().worker)

    def update(self):
        self.networker.download_bg(self._db_url, self._updated)

    def _updated(self, data):
        if not isinstance(data, QtNetwork.QNetworkReply.NetworkError):
            try:
                data = json.loads(data.data())
                data = self._verify(**data)

                with open(DB_FILE, 'w') as db:
                    json.dump(data, db)
                if data['location'] != self._db_url:
                    self._db_url = data['location']
                    self.update()
                else:
                    self._read_db()
            except:
                pass  # Ignore

    def _verify(self, message, signature):
        key = RSA.importKey(self._pub_key)
        h = SHA256.new()
        h.update(message)
        verifier = PKCS1_PSS.new(key)
        if verifier.verify(h, signature.decode('base64')):
            return json.loads(message.decode('base64'))
        raise ValueError("Invalid file signature!")

    def _read_db(self):
        try:
            with open(DB_FILE, 'r') as db:
                data = json.load(db)
        except:
            basedir = QtCore.QCoreApplication.instance().basedir
            path = os.path.join(basedir, 'appletdb.json')
            with open(path, 'r') as db:
                data = json.load(db)
        self._applets = []
        for applet in data['applets']:
            self._applets.append(Applet(**applet))
        self._hidden = data['hidden']
        self._db_url = data['location']
        self._pub_key = data['pubkey']

    def get_applets(self):
        return self._applets

    def get_applet(self, aid):
        if aid in self._hidden:
            return None
        for applet in self._applets:
            if aid.startswith(applet.aid):
                return applet
        return Applet(aid, m.unknown, m.unknown_applet)
