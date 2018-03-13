# -*- coding: utf8 -*-

from hashlib import sha1

from tuttle.report.html_repport import nice_size

try:
    from urllib2 import urlopen, Request, URLError, HTTPError, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, \
    build_opener, install_opener
except ImportError:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
from tuttle.error import TuttleError
from tuttle.resource import ResourceMixIn
from tuttle.version import version

try:
    import pycurl
except ImportError:
    pycurl = None


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

    def __init__(self):
        self._to_download = None

    @staticmethod
    def downloadable_resource(resource):
        downloadable_schemes = ['http', 'ftp', 'https']
        return resource.scheme in downloadable_schemes

    @staticmethod
    def contains_one_downloadable_resource(resources):
        nb_downloadables = 0
        for resource in resources:
            if DownloadProcessor.downloadable_resource(resource):
                nb_downloadables += 1
        return nb_downloadables == 1

    @staticmethod
    def the_downloadable_resource(inputs):
        result = None
        for resource in inputs:
            if DownloadProcessor.downloadable_resource(resource):
                if result is not None:
                    return False
                else:
                    result = resource
        return result

    def static_check(self, process):
        inputs = [res for res in process.iter_inputs()]
        outputs = [res for res in process.iter_outputs()]
        if len(outputs) != 1 \
           or outputs[0].scheme != 'file':
            raise TuttleError("Download processor {} don't know how to handle these outputs".format(process.id))
        if not DownloadProcessor.contains_one_downloadable_resource(inputs):
            raise TuttleError("Download processor {} don't know how to handle these inputs".format(process.id))

    def reader2writer(self, reader, writer, notifier):
        for chunk in iter(lambda: reader.read(32768), b''):
            writer.write(chunk)
            notifier.write('.')

    def run_urlopen(self, url, fout, notifier):
        headers = {"User-Agent": USER_AGENT}
        req = Request(url, headers=headers)
        fin = urlopen(req)
        self.reader2writer(fin, fout, notifier)

    def run_pycurl(self, to_download, fout, notifier):
        self._progress_b = 0
        self._progress_hMB = 0

        def show_progress(download_t, download_d, upload_t, upload_d):
            if download_d >= download_t and download_d > self._progress_b:
                notifier.write('.')
                self._progress_b = download_t
            elif download_d > self._progress_b + 32768:
                notifier.write('.')
                self._progress_b = download_d
            if download_d > self._progress_hMB + 100 * 1024 * 1024:
                self._progress_hMB = download_d
                notifier.write('\n{} / {}\n'.format(nice_size(self._progress_hMB), nice_size(download_t)))

        c = pycurl.Curl()
        c.setopt(c.URL, to_download.url)
        if to_download._user:
            c.setopt(pycurl.USERNAME, to_download._user)
        if to_download._password:
            c.setopt(pycurl.PASSWORD, to_download._password)
        c.setopt(pycurl.USERAGENT, USER_AGENT)
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.NOPROGRESS, False)
        c.setopt(c.XFERINFOFUNCTION, show_progress)
        c.setopt(c.WRITEDATA, fout)
        c.perform()
        c.close()

    def run(self, process, reserved_path, log_stdout, log_stderr):
        to_download = DownloadProcessor.the_downloadable_resource(process.iter_inputs())
        outputs = [res for res in process.iter_outputs()]
        file_name = outputs[0]._get_path()

        with open(file_name, 'wb') as fout, \
             open(log_stdout, 'wb') as stdout, \
             open(log_stderr, 'wb') as stderr:
            stdout.write("Downloading {}\n".format(to_download.url, file_name))
            if pycurl:
                self.run_pycurl(to_download, fout, stdout)
            stdout.write("\ndone\n ")
        return 0
