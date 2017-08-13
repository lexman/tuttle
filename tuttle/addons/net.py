# -*- coding: utf8 -*-

from hashlib import sha1
try:
    from urllib2 import urlopen, Request, URLError, HTTPError, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, \
    build_opener, install_opener
except ImportError:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
from tuttle.error import TuttleError
from tuttle.resource import ResourceMixIn
from tuttle.version import version


USER_AGENT = "tuttle/{}".format(version)


# TODO : should we follow resources in case of http redirection ?
class HTTPResource(ResourceMixIn, object):
    """An HTTP resource"""
    scheme = 'http' # Also https...
    password_manager = None  # Singleton

    def __init__(self, url):
        super(HTTPResource, self).__init__(url)

    def set_authentication(self, user, password):
        super(HTTPResource, self).set_authentication(user, password)
        if self.url.startswith("http"):
            if not HTTPResource.password_manager:
                HTTPResource.password_manager = HTTPPasswordMgrWithDefaultRealm()
                auth_handler = HTTPBasicAuthHandler(HTTPResource.password_manager)
                opener = build_opener(auth_handler)
                install_opener(opener)
            HTTPResource.password_manager.add_password(None, self.url, user, password)

    def exists(self):
        try:
            headers = {"User-Agent": USER_AGENT}
            req = Request(self.url, headers=headers)
            response = urlopen(req)
            some_data = response.read(0)
        except HTTPError as e:
            if e.code == 404:
                return False
            elif e.code == 401:
                msg = "Can't access {} because a password is needed. Configure a .tuttlepass file to set " \
                      "authentication for this resource".format(self.url)
                raise TuttleError(msg)
            else:
                msg = "An error occured while accessing {} : \n{}".format(self.url, str(e))
                raise TuttleError(msg)
        except URLError as e:
            # return False
            msg = "An error occured while accessing {} : \n{}".format(self.url, str(e))
            raise TuttleError(msg)
        return True

    def remove(self):
        raise TuttleError("HTTP resources can't be removed !")

    def get_header(self, info, header):
        for a_header in info.headers:
            if a_header.startswith(header):
                return a_header
        return None

    def signature(self):
        try:
            headers = {"User-Agent": USER_AGENT}
            req = Request(self.url, headers=headers)
            response = urlopen(req)
            info = response.info()
            etag = self.get_header(info, "Etag")
            if etag:
                # The most reliable is etag
                return etag.strip()
            lastmod = self.get_header(info, "Last-Modified")
            if lastmod:
                return lastmod.strip()
            lastmod = self.get_header(info, "Last-Modified")
            if lastmod:
                return lastmod.strip()
            # If we can't rely on the headers, then we compute
            # a hash from the beginning of the resource
            chunk_32k = response.read(32768)
            checksum = sha1()
            checksum.update(chunk_32k)
            return "sha1-32K: {}".format(checksum.hexdigest())
        except (URLError, HTTPError):
            return False


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
