# -*- coding: utf8 -*-

from time import sleep

from os import remove

from nose.plugins.skip import SkipTest
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from os.path import dirname, join, exists

from tests import online
from tuttle.addons.ftp import FTPResource
from tuttle.project_parser import ProjectParser


class TestFtpResource:

    ftpd = None
    p = None
    ftp_dir = join(dirname(__file__), 'ftp')

    @classmethod
    def run_server(cls):
        authorizer = DummyAuthorizer()
        authorizer.add_user("user", "password", cls.ftp_dir, perm="elrd")
        #authorizer.add_anonymous(ftp_dir, perm="elrd")
        handler = FTPHandler
        handler.authorizer = authorizer
        cls.ftpd = FTPServer(("0.0.0.0", 8021), handler)
        cls.ftpd.serve_forever(timeout=0.2, handle_exit=True)

    @classmethod
    def setUpClass(cls):
        """ Run a web server in background to mock some specific HTTP behaviours
        """
        from threading import Thread
        cls.p = Thread(target=cls.run_server)
        cls.p.start()
        sleep(0.1)  # The server needs time to start

    @classmethod
    def tearDownClass(cls):
        """ Stop the http server in background
        """
        cls.ftpd.close_all()
        cls.ftpd.ioloop.close()
        cls.p.join()
        to_rm = join(cls.ftp_dir, 'to_remove')
        if exists(to_rm):
            remove(to_rm)

    def test_resource_exists(self):
        """A mocked ftp resource should exist"""
        res = FTPResource("ftp://localhost:8021/ftp_resource")
        res.set_authentication("user", "password")
        assert res.exists()

    def test_missing_resource_should_not_exists(self):
        """A mocked ftp resource should exist"""
        res = FTPResource("ftp://localhost:8021/not_an_ftp_resource")
        res.set_authentication("user", "password")
        assert not res.exists()

    def test_raise_if_wrong_credentials(self):
        """A real resource should exist"""
        # Or by a local http server
        res = FTPResource("ftp://localhost:8021/ftp_resource_without_cred")
        res.set_authentication("user", "bad_password")
        try:
            res.exists()
            assert False, "exists should have raised"
        except:
            assert True

    def test_delete(self):
        """ When an ftp resource is deeted it shouldn't exist anymore"""
        with open(join(self.ftp_dir, 'to_remove'), 'w') as f:
            f.write("Will be removed\n")

        res = FTPResource("ftp://localhost:8021/to_remove")
        res.set_authentication("user", "password")
        assert res.exists()
        res.remove()
        assert not res.exists()

    def test_signature(self):
        """ Should return a signature for an ftp resource """
        res = FTPResource("ftp://localhost:8021/ftp_resource")
        res.set_authentication("user", "password")
        assert res.exists()
        s = res.signature()
        assert s == 'sha1-32K: 4627d1a3557c0c75698b70df9f17c8654f734f55', s

    def test_signature_raises_if_bad_credentials(self):
        """ If crendentials are wrong, signarue() should raise """
        res = FTPResource("ftp://localhost:8021/ftp_resource")
        res.set_authentication("user", "bad_password")
        try:
            s = res.signature()
            assert False, "signature should have raised"
        except:
            assert True

    def test_ftp_resource_in_workflow(self):
        """An HTTPS resource should be allowed in a workflow"""
        pp = ProjectParser()
        project = " <- ftp://localhost/ftp_resource"
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow._processes) == 1
        inputs = [res for res in workflow._processes[0].iter_inputs()]
        assert len(inputs) == 1

    def test_real_resource_exists(self):
        """A mocked ftp resource should exist"""
        if not online:
            raise SkipTest("Offline")
        #res = FTPResource("ftp://ftp.gnu.org/README")
        res = FTPResource("ftp://ftp.de.debian.org/debian//README")
        #res = FTPResource("ftp://ftp.mozilla.org/pub/firefox/releases/latest/README.txt")
        assert res.exists()
