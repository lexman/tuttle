# -*- coding: utf8 -*-

from tuttle.resources import FileResource

import tuttle.resources
from os import path

class TestHttpResource():

    def test_real_resource_exists(self):
        """A real resource should exist"""
        file_url = "file://{}".format(path.abspath(tuttle.resources.__file__))
        res = FileResource(file_url)
        assert res.exists()

    def test_fictive_resource_exists(self):
        """A real resource should exist"""
        res = FileResource("fictive_file")
        assert not res.exists()
