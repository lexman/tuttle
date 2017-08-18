# -*- coding: utf8 -*-
from hashlib import sha1

import sys
from re import compile

try:
    from urllib2 import urlopen, Request, URLError, HTTPError, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, \
    build_opener, install_opener
except ImportError:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
from tuttle.error import TuttleError
from tuttle.resource import ResourceMixIn, MalformedUrl
from tuttle.version import version
from ftplib import FTP


USER_AGENT = "tuttle/{}".format(version)


# TODO : should we follow resources in case of http redirection ?
class FTPResource(ResourceMixIn, object):
    """An HTTP resource"""
    scheme = 'ftp'

    __ereg = compile("^ftp://([^/^:]*)(:[0-9]*)?/(.*)$")


    def __init__(self, url):
        super(FTPResource, self).__init__(url)
        m = self.__ereg.match(url)
        if m is None:
            raise MalformedUrl("Malformed FTP url : '{}'".format(url))
        self._host = m.group(1)
        captured_port = m.group(2)
        if captured_port:
            self._port = captured_port[1:]
        else:
            self._host = 21
        self._partial = m.group(3)
        self._authenticated_url = self.url

    def set_authentication(self, user, password):
        super(FTPResource, self).set_authentication(user, password)
        self._authenticated_url = 'ftp://{}:{}@{}'.format(self._user, self._password, self.url[6:])

    def exists(self):
        try:
            req = Request(self._authenticated_url)
            response = urlopen(req)
            some_data = response.read(0)
        except URLError as e:
            if e.reason.find("550") > -1:
                return False
            msg = "An error occured while accessing {} : \n{}".format(self.url, str(e))
            raise TuttleError(msg)
        return True

    def remove(self):
        ftp = FTP()
        ftp.connect(self._host, self._port)
        if self._user or self._password:
            ftp.login(self._user, self._password)
        ftp.delete(self._partial)
        ftp.close()

    def signature(self):
        # There are so many implementations of ftp it's hard to find a common way to even
        # retrieve the size of the file. That's why we fallback to a short hash
        try:
            req = Request(self._authenticated_url)
            response = urlopen(req)
            # a hash from the beginning of the resource
            chunk_32k = response.read(32768)
            checksum = sha1()
            checksum.update(chunk_32k)
            return "sha1-32K: {}".format(checksum.hexdigest())
        except URLError as e:
            return TuttleError("Can't compute signature for {}. Error was : {}".format(self.url, str(e)))


class DownloadProcessor:
    """ A processor for downloading http resources
    """
    name = 'download'

    def static_check(self, process):
        inputs = [res for res in process.iter_inputs()]
        outputs = [res for res in process.iter_outputs()]
        if len(inputs) != 1 \
           or len(outputs) != 1 \
           or inputs[0].scheme != 'http' \
           or outputs[0].scheme != 'file':
            raise TuttleError("Download processor {} don't know how to handle his inputs / outputs".format(process.id))

    def reader2writer(self, reader, writer, notifier):
        for chunk in iter(lambda: reader.read(32768), b''):
            writer.write(chunk)
            notifier.write('.')

    def run(self, process, reserved_path, log_stdout, log_stderr):
        inputs = [res for res in process.iter_inputs()]
        outputs = [res for res in process.iter_outputs()]
        file_name = outputs[0]._get_path()
        url = inputs[0].url
        headers = {"User-Agent": USER_AGENT}
        req = Request(url, headers=headers)
        fin = urlopen(req)
        with open(file_name, 'wb') as fout, \
             open(log_stdout, 'wb') as stdout, \
             open(log_stderr, 'wb') as stderr:
            stdout.write("Downloading {}\n".format(url, file_name))
            self.reader2writer(fin, fout, stdout)
            stdout.write("\ndone\n ")
        return 0
