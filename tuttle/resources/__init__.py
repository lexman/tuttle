#!/usr/bin/env python
# -*- coding: utf8 -*-

from os.path import abspath, exists
from os import remove
from tuttle.error import TuttleError

from tuttle import __version__
from urllib2 import Request, urlopen, URLError, HTTPError


class MalformedUrl(TuttleError):
    pass


class ResourceMixIn:
    """ Common behaviour for all resources """

    def __init__(self, url):
        self.url = url
        self.creator_process = None

    def set_creator_process(self, process):
        self.creator_process = process

    def is_primary(self):
        """ Returns True if the resources is a primary resource, ie if it not computed by tuttle but is needed
        to compute other resources.
        This information is meaningful only in a workflow context : it is valid only after
        a call to workflow.compute_dependancies()
        :return: True if resource is a primary resource
        """
        return self.creator_process is None


class FileResource(ResourceMixIn, object):
    """A resource for a local file"""
    scheme = 'file'

    def __init__(self, url):
        super(FileResource, self).__init__(url)
        self._path = self._get_path()

    def _get_path(self):
        return abspath(self.url[len("file://"):])

    def exists(self):
        return exists(self._path)

    def remove(self):
        remove(self._path)


class HTTPResource(ResourceMixIn, object):
    """An HTTP resource"""
    scheme = 'http'
    user_agent = "tuttle/{}".format(__version__)

    def __init__(self, url):
        super(HTTPResource, self).__init__(url)

    def exists(self):
        try:
            headers = {"User-Agent" : self.user_agent}
            req = Request(self.url, headers = headers)
            response = urlopen(req)
            some_data = response.read(0)
        except (URLError, HTTPError):
            return False
        return True

    def remove(self):
        raise TuttleError("HTTP resources can't be removed !")
