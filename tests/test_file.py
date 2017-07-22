# -*- coding: utf-8 -*-

from tests.functional_tests import isolate
from tuttlelib.resources import FileResource
import os


# TODO what about symlinks ?
class TestFile():


    @isolate
    def test_directory_should_be_removable(self):
        """ if a file resource is a directory it should be removable """
        os.mkdir('a_dir')
        assert os.path.isdir('a_dir')
        r = FileResource("file://a_dir")
        r.remove()
        assert not os.path.exists('a_dir')

    @isolate
    def test_directory_should_be_removable_even_if_not_empty(self):
        """ if a file resource is a directory it should be removable even if it contains files """
        os.mkdir('a_dir')
        open('a_dir/A', 'w').write('A')
        assert os.path.isdir('a_dir')
        r = FileResource("file://a_dir")
        r.remove()
        assert not os.path.exists('a_dir')

    @isolate
    def test_directory_should_have_a_signature(self):
        """ if a file resource is a directory it should be removable """
        os.mkdir('a_dir')
        assert os.path.isdir('a_dir')
        r = FileResource("file://a_dir")
        sig = r.signature()
        # TODO should a directory have a signature resulting of its content ?
        assert sig.startswith("sha1:"), sig
