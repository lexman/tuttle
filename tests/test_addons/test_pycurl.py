# -*- coding: utf8 -*-
import pycurl
from StringIO import StringIO


class TestPyCurl:

    def test_fictive_resource_not_exists(self):
        """A fictive resource should not exist"""
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'http://pycurl.io/')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        # Body is a string in some encoding.
        # In Python 2, we can print it without knowing what the encoding is.
        assert body.find("PycURL documentation") > -1, body
