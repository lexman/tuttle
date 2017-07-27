# -*- coding: utf8 -*-
from tempfile import mkdtemp
from shutil import rmtree, copytree, copy
from os.path import isdir, join, isfile
from tests.functional_tests import isolate, run_tuttle_file
from tuttlelib.commands import invalidate_resources

from tuttlelib.resources import FileResource
import tuttlelib.resources
from os import path, listdir
from tuttlelib.utils import CurrentDir


def copycontent(src, dst):
    for elmt in listdir(src):
        src_elmt = join(src, elmt)
        dst_elmt = join(dst, elmt)
        if isdir(elmt):
            copytree(src_elmt, dst_elmt)
        else:
            copy(src_elmt, dst_elmt)

class TestHttpResource():

    def test_real_resource_exists(self):
        """A real resource should exist"""
        file_url = "file://{}".format(path.abspath(tuttlelib.resources.__file__))
        res = FileResource(file_url)
        assert res.exists()

    def test_fictive_resource_exists(self):
        """A real resource should exist"""
        res = FileResource("fictive_file")
        assert not res.exists()

    @isolate(['A'])
    def test_relative_resource_is_attached_to_tuttlefile(self):
        """If you move a whole project, it must still work"""
        project = """file://B <- file://A
        echo A produces B >B
        echo A produces B
        """""
        run_tuttle_file(project)
        assert isfile('B')
        tmp_dir = mkdtemp()
        copycontent('.', tmp_dir)
        assert isfile(join(tmp_dir, 'B'))
        with CurrentDir(tmp_dir):
            invalidate_resources(join(tmp_dir, 'tuttlefile'), ['file://B'])
        assert isfile('B'), "File B in the origin project should still exist"
        assert not isfile(join(tmp_dir, 'B')), "File B in the copied project should have been removed"

