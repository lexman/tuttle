# -*- coding: utf8 -*-

from time import sleep
from os.path import dirname, join, abspath
from urllib import urlretrieve

from nose.plugins.skip import SkipTest

from tuttle.addons.hdfs import HDFSResource
from tuttle.project_parser import ProjectParser
from snakebite.minicluster import MiniCluster


class TestHdfsResource:

    #testfiles_path = join(dirname(abspath(__file__)), "testfiles")
    testfiles_path = dirname(abspath(__file__))
    cluster = None

    @classmethod
    def setUpClass(cls):
        if not cls.cluster:
            c = MiniCluster(None, start_cluster=False)
            result = c.ls("/")
            if result:
                raise Exception("An active Hadoop cluster is found! Not running tests!")

            cls.cluster = MiniCluster(cls.testfiles_path)
            result = cls.cluster.ls("/")
            if result:
                raise Exception("An active Hadoop cluster is found! Not running tests!")
            cls.cluster.put("/A", "/A")
            cls.cluster.put("/A", "/file_to_be_deleted")
            cls.cluster.mkdir("/dir")
            cls.cluster.mkdir("/dir_to_be_deleted")
            cls.cluster.put("/A", "/dir_to_be_deleted/inside_dir")

    @classmethod
    def tearDownClass(cls):
        if cls.cluster:
            cls.cluster.terminate()

    def test_file_resource_exists(self):
        """A mocked hdfs file resource should exist"""
        res = HDFSResource("hdfs://localhost:{}/A".format(self.cluster.port))
        assert res.exists()

    def test_directory_resource_exists(self):
        """A mocked hdfs directory resource should exist"""
        res = HDFSResource("hdfs://localhost:{}/dir".format(self.cluster.port))
        assert res.exists()

    def test_resource_not_exists(self):
        """An hdfs resource not mocked should not exist"""
        res = HDFSResource("hdfs://localhost:{}/B".format(self.cluster.port))
        assert not res.exists()

    def test_resource_with_bad_credentials_should_raise(self):
        """ An hdfs resource with bad credentials should raise """
        raise SkipTest()  # Minicluster does not seam to implement authentication. Does snakebite ?
        res = HDFSResource("hdfs://localhost:{}/A".format(self.cluster.port))
        res.set_authentication('foo', 'bar')
        try:
            res.exists()
            assert False, "exists should have raised"
        except:
            assert True

    def test_delete_file(self):
        """ When an hdfs resource is deleted it shouldn't exist anymore"""
        res = HDFSResource("hdfs://localhost:{}/file_to_be_deleted".format(self.cluster.port))
        assert res.exists()
        res.remove()
        assert not res.exists()

    def test_delete_dir(self):
        """ An hdfs directory can be deleted, even if not empty """
        res = HDFSResource("hdfs://localhost:{}/dir_to_be_deleted".format(self.cluster.port))
        assert res.exists()
        res.remove()
        assert not res.exists()

    def test_file_signature(self):
        """ An hdfs file has a signature """
        res = HDFSResource("hdfs://localhost:{}/A".format(self.cluster.port))
        assert res.signature().startswith("modification_time:"), res.signature()

    def test_dir_signature(self):
        """ An hdfs file has a signature """
        res = HDFSResource("hdfs://localhost:{}/dir".format(self.cluster.port))
        assert res.signature() == "d", res.signature()


def install_hadoop():
    import zipfile
    urlretrieve("http://apache.mediamirrors.org/hadoop/common/hadoop-2.8.1/hadoop-2.8.1.tar.gz", "hadoop-2.8.1.tar.gz")
    zip = zipfile.ZipFile("hadoop-2.8.1.tar.gz")
    zip.extractall("hadoop-2.8.1")
