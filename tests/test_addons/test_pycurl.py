# -*- coding: utf8 -*-
import pycurl
import sys
from unittest.case import SkipTest

from tests import online


class TestPyCurl:

    def test_pycurl_download_progress(self):
        if not online:
            raise SkipTest("Can't test download offline")
        def progress(download_t, download_d, upload_t, upload_d):
            print("Total to download {}\n".format(download_t))
            print("Total downloaded {}\n".format(download_d))
            print("Total to upload {}\n".format(upload_t))
            print("Total uploaded {}\n".format(upload_d))

        with open('out.html', 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, 'http://pycurl.io/')
            #c.setopt(c.URL, 'http://planet.osm.org/pbf/planet-latest.osm.pbf')
            c.setopt(pycurl.USERAGENT, "python test")
            c.setopt(c.NOPROGRESS, False)
            c.setopt(c.XFERINFOFUNCTION, progress)
            c.setopt(c.WRITEDATA, f)
            c.perform()
            c.close()

