# -*- coding: utf8 -*-
from shutil import rmtree

from os.path import abspath, exists, isfile
from os import remove
from hashlib import sha1
from tuttle.error import TuttleError


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
        a call to workflow.compute_dependencies()
        :return: True if resource is a primary resource
        """
        return self.creator_process is None

    def created_by_same_inputs(self, other_resource):
        """
        Call to depends_on_same_inputs is valid only if both resources are not primary (ie creator_process exists !)
        """
        self_inputs = self.creator_process.input_urls()
        other_inputs = other_resource.creator_process.input_urls()
        return self_inputs == other_inputs


def hash_file(file_like_object):
    """Generate a hash for the contents of a file."""
    checksum = sha1()
    for chunk in iter(lambda: file_like_object.read(32768), b''):
        checksum.update(chunk)
    return checksum.hexdigest()


class FileResource(ResourceMixIn, object):
    """A resource for a local file"""
    scheme = 'file'

    def __init__(self, url):
        super(FileResource, self).__init__(url)

    def _get_path(self):
        return abspath(self.url[len("file://"):])

    def exists(self):
        return exists(self._get_path())

    def signature(self):
        sha1 = None
        try:
            with open(self._get_path()) as f:
                sha1 = hash_file(f)
        except IOError:
            pass
        return "sha1:{}".format(sha1)

    def remove(self):
        path = self._get_path()
        if isfile(path):
            remove(path)
        else:
            #directory
            rmtree(path)
        # TODO what about links ?