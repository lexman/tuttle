# -*- coding: utf8 -*-
from os import remove, getcwd
from os.path import dirname, join, abspath, exists
from urllib import urlretrieve
from nose.plugins.skip import SkipTest
from setuptools.archive_util import unpack_tarfile

from tuttle.addons.hdfs import HDFSResource
from snakebite.minicluster import MiniCluster
import sys, os

class TestHdfsResource:

    #testfiles_path = join(dirname(abspath(__file__)), "testfiles")
    testfiles_path = dirname(abspath(__file__))
    cluster = None

    @classmethod
    def setUpClass(cls):
        if 'HADOOP_HOME' not in os.environ or not os.environ['HADOOP_HOME']:
            raise SkipTest("Hadoop not installed")

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
    try:
        import tests
        hadoop_path = join(dirname(tests.__file__), 'hadoop')
    except:
        hadoop_path = join('tests', 'hadoop')
    if not exists(hadoop_path):
        print("Installing hadoop 2.9.0 in {}".format(hadoop_path))
        url = "http://apache.mediamirrors.org/hadoop/common/stable2/hadoop-2.9.0.tar.gz"
        if not exists("hadoop-2.9.0.tar.gz"):
            print("Downloading from {} to {}".format(url, getcwd()))
            urlretrieve(url, "hadoop-2.9.0.tar.gz")
        print("Unzipping to {}".format(hadoop_path))
        unpack_tarfile("hadoop-2.9.0.tar.gz", hadoop_path)
        if os.name=="posix":
            with open(join(hadoop_path, "vars.sh"), "w") as f:
                f.write('export HADOOP_HOME="{}"\n'.format(join(hadoop_path, "hadoop-2.9.0")))
        if os.name=="nt":
            with open(join(hadoop_path, "vars.bat"), "w") as f:
                f.write('HADOOP_HOME="{}"\n'.format(join(hadoop_path, "hadoop-2.9.0")))
        remove("hadoop-2.9.0.tar.gz")

    else:
        print("Hadoop already installed in {}".format(hadoop_path))


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'install':
        install_hadoop()
