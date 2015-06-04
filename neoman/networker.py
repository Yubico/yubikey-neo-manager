from PySide import QtCore, QtNetwork
from time import sleep


class NetWorker:

    def __init__(self, worker):
        self._done = None
        self._dl = None
        self._worker = worker
        self._manager = QtNetwork.QNetworkAccessManager()
        self._manager.finished.connect(self._dl_done)

    def download(self, url, callback=None):
        self._done = False

        def mark_done(result):
            self._done = True
            callback(result)

        def dl():
            self.download_bg(url, mark_done)
            while not self._done:
                sleep(0.1)
        self._worker.post('Downloading...', dl)

    def download_bg(self, url, callback=None):
        print 'download_bg start'
        url = QtCore.QUrl(url)
        request = QtNetwork.QNetworkRequest(url)
        response = self._manager.get(request)
        self._dl = (request, response, callback)
        print 'download_bg done'

    def _dl_done(self):
        print 'dl done' # TODO: Never getting here
        (req, resp, callback) = self._dl
        del self._dl
        if callback:
            result = resp.error()
            if result is QtNetwork.QNetworkReply.NoError:
                result = resp.readAll()
            resp.close()
            callback(result)