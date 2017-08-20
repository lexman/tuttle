# -*- coding: utf8 -*-
from hashlib import sha1

import sys
from re import compile

from tuttle.error import TuttleError
from tuttle.resource import ResourceMixIn, MalformedUrl
from snakebite.client import Client

class HDFSResource(ResourceMixIn, object):
    """An HTTP resource"""
    scheme = 'hdfs'

    __ereg = compile("^hdfs://([^/^:]*)(:[0-9]*)?(/.*)$")

    def __init__(self, url):
        super(HDFSResource, self).__init__(url)
        m = self.__ereg.match(url)
        if m is None:
            raise MalformedUrl("Malformed HDFS url : '{}'".format(url))
        self._host = m.group(1)
        captured_port = m.group(2)
        if captured_port:
            self._port = int(captured_port[1:])
        else:
            self._port = 8020
        self._partial = m.group(3)

    def set_authentication(self, user, password):
        super(HDFSResource, self).set_authentication(user, password)

    def exists(self):
        client = Client(self._host, self._port, effective_user=self._user, use_trash=False)
        return client.test(self._partial, exists=True)

    def remove(self):
        client = Client(self._host, self._port, effective_user=self._user, use_trash=False)
        it = client.delete([self._partial], recurse=True)
        for elmt in it:
            pass

    def signature(self):
        client = Client(self._host, self._port, effective_user=self._user, use_trash=False)
        stats = client.stat([self._partial])
        if stats['file_type'] == 'f':
            return "modification_time:{}".format(stats['modification_time'])
        else:
            return stats['file_type']
