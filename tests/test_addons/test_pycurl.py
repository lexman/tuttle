# -*- coding: utf8 -*-
import pycurl
import sys

class TestPyCurl:

    def test_pycurl_download_progress(self):
        def progress(download_t, download_d, upload_t, upload_d):
            sys.stderr.write("Total to download {}\n".format(download_t))
            sys.stderr.write("Total downloaded {}\n".format(download_d))
            sys.stderr.write("Total to upload {}\n".format(upload_t))
            sys.stderr.write("Total uploaded {}\n".format(upload_d))

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

