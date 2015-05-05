# -*- coding: utf8 -*-

from urllib2 import Request, urlopen, URLError, HTTPError
from tuttle.error import TuttleError
from tuttle.resources import ResourceMixIn

version = "0.1"

USER_AGENT = "tuttle/{}".format(version)


class HTTPResource(ResourceMixIn, object):
    """An HTTP resource"""
    scheme = 'http'

    def __init__(self, url):
        super(HTTPResource, self).__init__(url)

    def exists(self):
        try:
            headers = {"User-Agent" : USER_AGENT}
            req = Request(self.url, headers = headers)
            response = urlopen(req)
            some_data = response.read(0)
        except (URLError, HTTPError):
            return False
        return True

    def remove(self):
        raise TuttleError("HTTP resources can't be removed !")

    def signature(self):
        return ""


class DownloadProcessor:
    """ A processor for downloading http resources
    """
    name = 'download'

    def pre_check(self, process):
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
        # TODO how do we handle errors ?
        inputs = [res for res in process.iter_inputs()]
        outputs = [res for res in process.iter_outputs()]
        file_name = outputs[0]._path
        url = inputs[0].url
        headers = {"User-Agent" : USER_AGENT}
        req = Request(url, headers = headers)
        fin = urlopen(req)
        with open(file_name, 'wb') as fout, \
             open(log_stdout, 'wb') as stdout, \
             open(log_stderr, 'wb') as stderr:
            stdout.write("Downloading {}\n".format(url, file_name))
            self.reader2writer(fin, fout, stdout)
            stdout.write("\ndone\n ")
        return 0

