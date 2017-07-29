# -*- coding: utf8 -*-
from tempfile import mkdtemp
from shutil import rmtree
from os import makedirs, environ
from os.path import join
from tests.functional_tests import isolate, run_tuttle_file
from s3server import start
from tuttle.project_parser import ProjectParser
from tuttle.extensions.s3 import S3Resource

class TestS3Resource():

    server_thread = None

    @classmethod
    def run_server(cls):
        cls.tmp_dir = mkdtemp()
        bucket_dir = join(cls.tmp_dir, "test_bucket")
        makedirs(bucket_dir)
        test_key_file = join(bucket_dir, "test_key")
        open(test_key_file, "w").close()
        key_for_removal = join(bucket_dir, "key_for_removal")
        open(key_for_removal, "w").close()
        start(8069, root_directory=cls.tmp_dir)

    @classmethod
    def setUpClass(cls):
        """ Run a S3 compatible server mock
        """
        from threading import Thread
        cls.server_thread = Thread(target=cls.run_server)
        cls.server_thread.start()
        # Set environment variable to ensure client authentication
        environ['AWS_ACCESS_KEY_ID'] = "MY_AWS_ACCOUNT"
        environ['AWS_SECRET_ACCESS_KEY'] = "MY_AWS_PASSWORD"

    @classmethod
    def tearDownClass(cls):
        """ Stop the S3 server in background
        """
        from time import sleep
        from tornado import ioloop
        ioloop.IOLoop.current().stop()
        rmtree(cls.tmp_dir)

    def test_resource_properties(self):
        """An s3 resource should have an endpoint, a bucket and a key"""
        res = S3Resource("s3://localhost:8069/test_bucket/test_key")
        assert res._endpoint == 'http://localhost:8069', res._endpoint
        assert res._bucket == 'test_bucket', res._bucket
        assert res._key == 'test_key', res._key

    def test_real_resource_exists(self):
        """A real s3 resource should exist"""
        res = S3Resource("s3://localhost:8069/test_bucket/test_key")
        assert res.exists()

    def test_fictive_resource_not_exists(self):
        """A fictive resource should not exist"""
        res = S3Resource("s3://localhost:8069/test_bucket/i_dont_exist")
        assert not res.exists()

    def test_s3_resource_in_workflow(self):
        """An s3 resource should be allowed in a workflow"""
        pp = ProjectParser()
        project = "<- s3://localhost:8069/test_bucket/test_key"
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow._processes) == 1
        inputs = [res for res in workflow._processes[0].iter_inputs()]
        assert len(inputs) == 1, len(inputs)
        assert inputs[0].scheme == "s3", inputs[0].scheme

    def test_resource_signature(self):
        """ An S3 signature is the Etag of the web object"""
        res = S3Resource("s3://localhost:8069/test_bucket/test_key")
        sig = res.signature()
        assert sig == '"da39a3ee5e6b4b0d3255bfef95601890afd80709"', sig

    def test_remove_s3_resource(self):
        """remove() should remove the resource"""
        res = S3Resource("s3://localhost:8069/test_bucket/key_for_removal")
        assert res.exists()
        res.remove()
        assert not res.exists()

    def test_when_host_is_unknown_resource_should_not_exist(self):
        """If the host is unknown or invalid, resource should be considered as non existant"""
        res = S3Resource("s3://localhost2:8069/test_bucket/test_key")
#        assert not res.exists()

    # TODO
    # Maybe we can create a specific tuttle exception that could also be valid at least
    # with postgresql resources. Usable for files ?
    def test_invalid_credential_should_make_resource_not_exist(self):
        """If """
        del environ['AWS_ACCESS_KEY_ID']
        del environ['AWS_SECRET_ACCESS_KEY']
        try:
            res = S3Resource("s3://localhost:8069/test_bucket/test_key")
            assert not res.exists()
        finally:
            environ['AWS_ACCESS_KEY_ID'] = "MY_AWS_ACCOUNT"
            environ['AWS_SECRET_ACCESS_KEY'] = "MY_AWS_PASSWORD"
