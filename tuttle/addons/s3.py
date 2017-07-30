# -*- coding: utf8 -*-

from re import compile

from tuttle.addons.netutils import hostname_resolves
from tuttle.error import TuttleError
from tuttle.resources import ResourceMixIn, MalformedUrl
from tuttle.version import version
from boto3.session import Session
from botocore.exceptions import ClientError, BotoCoreError


USER_AGENT = "tuttle/{}".format(version)


class S3Resource(ResourceMixIn, object):
    """An S3 resource"""
    scheme = 's3'

    ereg = compile("^s3://([^/]+)/([^/]+)/(.+)$")

    def __init__(self, url):
        super(S3Resource, self).__init__(url)
        m = self.ereg.match(url)
        if m is None:
            raise MalformedUrl("Malformed S3 url : '{}'".format(url))
        self._host = m.group(1).split(':')[0]
        self._endpoint = "http://{}".format(m.group(1))
        self._bucket = m.group(2)
        self._key = m.group(3)

    def _object(self):
        session = Session()
        s3 = session.resource('s3', endpoint_url=self._endpoint)
        obj = s3.Object(self._bucket, self._key)
        return obj

    def exists(self):
        if not hostname_resolves(self._host):
            raise TuttleError("Unknown host : \"{}\"... "
                              "Can't check existence of resource {}.".format(self._host, self.url))

        object = self._object()
        try:
            res = object.get()
            return True
        except (ClientError, BotoCoreError) as e:
            return False

    def remove(self):
        object = self._object()
        object.delete()

    def signature(self):
        object = self._object()
        try:
            res = object.get()
            return res[u'ETag']
        except (ClientError, BotoCoreError) as e:
            return False
