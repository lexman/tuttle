# -*- coding: utf8 -*-

from hashlib import sha1
from re import compile
from urllib2 import urlopen, Request, URLError
from tuttle.error import TuttleError
from tuttle.resource import ResourceMixIn, MalformedUrl
from ftplib import FTP


class FTPResource(ResourceMixIn, object):
    """An FTP resource"""
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
