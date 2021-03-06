# -*- coding: utf8 -*-
import BaseHTTPServer
import SocketServer
import re
import socket
from os.path import isfile, join, dirname, isdir
from time import sleep

from nose.plugins.skip import Skip, SkipTest

from tests.functional_tests import isolate, run_tuttle_file, tuttle_invalidate
from tuttle.error import TuttleError
from tuttle.project_parser import ProjectParser
from tuttle.addons.net import HTTPResource
from BaseHTTPServer import BaseHTTPRequestHandler
from SocketServer import TCPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from tuttle.tuttle_directories import TuttleDirectories
from tuttle.utils import EnvVar
from tuttle.workflow_runner import WorkflowRunner
from tuttle import report
from tests import is_online, online


class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
                          SocketServer.TCPServer,
                          BaseHTTPServer.HTTPServer):
    pass


class MockHTTPHandler(BaseHTTPRequestHandler):
    """ This class is used to mock some HTTP behaviours :
    * Etag
    * Last-Modified
    * Neither
    Useful both for running tests offline and for not depending on some external change
    """

    viz = join(dirname(report.__file__), 'html_report_assets', 'viz.js')

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def handle(self):
        try:
            BaseHTTPRequestHandler.handle(self)
        except socket.error:
            pass

    def finish(self, *args, **kw):
        try:
            if not self.wfile.closed:
                self.wfile.flush()
                self.wfile.close()
        except socket.error:
            pass
        self.rfile.close()

    def log_message(self, format, *args):
        # Don't log
        return

    def do_GET(self):
        if self.path == "/protected_resource":
            auth = self.headers.get('Authorization', False)
            if auth:
                self.send_response(200, "OK")
                self.send_header('Content-type', 'text/plain')
                self.send_header('Etag', auth)
                self.end_headers()
                self.wfile.write("Authentication provided : {}".format(auth))
            else:
                self.send_response(401, "Authentication required")
                self.send_header('WWW-Authenticate', 'BASIC realm="foo"')
                self.end_headers()
                self.wfile.write("Please provide user and password in BASIC authentication")
        if self.path == "/unavailable_protected_resource":
            self.send_response(401, "Authentication required")
            self.send_header('WWW-Authenticate', 'BASIC realm="foo"')
            self.end_headers()
            self.wfile.write("Please provide user and password in BASIC authentication")
        if self.path == "/a_resource":
            self.send_response(200, "OK")
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("This is a resource")
        if self.path == "/resource_with_etag":
            self.send_response(200, "OK")
            self.send_header('Etag', 'my_etag')
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("This resource provides an Etag")
        if self.path == "/resource_with_last_modified":
            self.send_response(200, "OK")
            self.send_header('Last-Modified', 'Tue, 30 Jun 1981 03:14:59 GMT')
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("This resource provides a Last-Modified")
        if self.path == "/resource_without_version":
            self.send_response(200, "OK")
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("This resource has no version information")
        if self.path == "/huge_resource.js":
            self.send_response(200, "OK")
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            with open(self.viz) as f:
                content = f.read()
                try:
                    self.wfile.write(content)
                except Exception:
                    pass


class TestHttpResource:

    httpd = None
    p = None

    @classmethod
    def run_server(cls):
        cls.httpd = ThreadingHTTPServer(("", 8042), MockHTTPHandler)
        cls.httpd.allow_reuse_address = True
        cls.httpd.serve_forever()

    @classmethod
    def setUpClass(cls):
        """ Run a web server in background to mock some specific HTTP behaviours
        """
        from threading import Thread
        cls.p = Thread(target=cls.run_server)
        cls.p.start()

    @classmethod
    def tearDownClass(cls):
        """ Stop the http server in background
        """
        cls.httpd.shutdown()
        cls.p.join()

    def test_real_resource_exists(self):
        """A real resource should exist"""
        # TODO : change this when tuttle has its site... If it can handle the load...
        # Or by a local http server
        if not online:
            raise SkipTest("Offline")
        res = HTTPResource("http://www.google.com/")
        assert res.exists()

    def test_fictive_resource_not_exists(self):
        """A fictive resource should not exist"""
        if not online:
            raise SkipTest("Offline")
        res = HTTPResource("http://www.example.com/tuttle")
        assert not res.exists()

    def test_http_resource_in_workflow(self):
        """An HTTP resource should be allowed in a workflow"""
        pp = ProjectParser()
        project = "file://result <- http://www.google.com/"
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow._processes) == 1
        inputs = [res for res in workflow._processes[0].iter_inputs()]
        assert len(inputs) == 1

    # TODO : should we follow resources in case of http redirection ?
    def test_resource_etag_signature(self):
        """ An HTTPResource with an Etag should use it as signature """
        res = HTTPResource("http://www.example.com/")
        sig = res.signature()
        if sig is False:
            raise SkipTest()
        assert sig.find('Etag:') >= 0, sig
        assert sig.find('1541025663') >= 0, sig

    def test_resource_last_modified_signature(self):
        """ An HTTPResource with an Last-Modified should use it as signature in case it doesn't have Etag"""
        # res = HTTPResource("http://www.wikipedia.org/")
        res = HTTPResource("http://localhost:8042/resource_with_last_modified")
        sig = res.signature()
        assert sig == 'Last-Modified: Tue, 30 Jun 1981 03:14:59 GMT', sig

    def test_ressource_with_authentication(self):
        """ Provided authentication should be used to access an http resource """
        res = HTTPResource("http://localhost:8042/protected_resource")
        res.set_authentication("user", "password")
        assert res.exists(), "http://localhost:8042/protected_resource should exists"
        sig = res.signature()
        assert sig == 'Etag: Basic dXNlcjpwYXNzd29yZA==', sig

    def test_ressource_with_bad_authentication(self):
        """ Wrong authentication should make tuttle fail """
        res = HTTPResource("http://localhost:8042/unavailable_protected_resource")
        res.set_authentication("user", "password")
        try:
            res.exists()
            assert False, "http://localhost:8042/unavailable_protected_resource is not meant to be available"
        except TuttleError as e:
            assert True


class TestHttpsResource:

    def test_real_resource_exists(self):
        """A real resource should exist"""
        if not online:
            raise SkipTest("Offline")
        res = HTTPResource("https://www.google.com/")
        assert res.exists()

    def test_fictive_resource_not_exists(self):
        """A fictive resource should not exist"""
        if not online:
            raise SkipTest("Offline")
        res = HTTPResource("https://www.example.com/tuttle")
        assert not res.exists()

    def test_http_resource_in_workflow(self):
        """An HTTPS resource should be allowed in a workflow"""
        pp = ProjectParser()
        project = "file://result <- https://www.google.com/"
        pp.set_project(project)
        workflow = pp.parse_project()
        assert len(workflow._processes) == 1
        inputs = [res for res in workflow._processes[0].iter_inputs()]
        assert len(inputs) == 1


class TestDownloadProcessor:

    httpd = None
    p = None
    _ftpd = None

    @classmethod
    def run_server(cls):
        cls.httpd = ThreadingHTTPServer(("", 8043), MockHTTPHandler)
        cls.httpd.allow_reuse_address = True
        cls.httpd.serve_forever()

    @classmethod
    def setUpClass(cls):
        """ Run a web server in background to mock some specific HTTP behaviours
        """
        from threading import Thread
        cls.p = Thread(target=cls.run_server)
        cls.p.start()

    @classmethod
    def tearDownClass(cls):
        """ Stop the http server in background
        """
        cls.httpd.shutdown()
        cls.p.join()

    @isolate
    def test_standard_download(self):
        """Should download a simple url"""
        if not online:
            raise SkipTest("Offline")
        project = " file://google.html <- http://www.google.com/ ! download"
        pp = ProjectParser()
        pp.set_project(project)
        workflow = pp.parse_extend_and_check_project()
        workflow.static_check_processes()
        workflow.discover_resources()
        TuttleDirectories.straighten_out_process_and_logs(workflow)
        wr = WorkflowRunner(3)
        wr.run_parallel_workflow(workflow)
        assert isfile("google.html")
        content = open("google.html").read()
        assert content.find("<title>Google</title>") >= 0
        logs = open(join(".tuttle", "processes", "logs", "__1_stdout.txt"), "r").read()
        assert re.search("\n\.+\n", logs) is not None, logs
        assert isfile(join(".tuttle", "processes", "logs", "__1_err.txt"))

    @isolate
    def test_long_download(self):
        """ Progress dots should appear in the logs in a long download"""
        project = " file://huge_resource.js <- http://localhost:8043/huge_resource.js ! download"
        pp = ProjectParser()
        pp.set_project(project)
        workflow = pp.parse_extend_and_check_project()
        workflow.static_check_processes()
        workflow.discover_resources()
        TuttleDirectories.straighten_out_process_and_logs(workflow)
        wr = WorkflowRunner(3)
        wr.run_parallel_workflow(workflow)
        assert isfile("huge_resource.js"), "huge_resource.js is missing"
        logs = open(join(".tuttle", "processes", "logs", "__1_stdout.txt"), "r").read()
        assert logs.find("...") >= 0

    @isolate
    def test_pre_check_outputs(self):
        """Should fail if don't know what to download """
        project = " file://foo <- ! download"
        pp = ProjectParser()
        pp.set_project(project)
        try:
            workflow = pp.parse_extend_and_check_project()
            assert False, "An exception should be raised"
        except TuttleError as e:
            assert e.message.find("don't know how to handle these inputs") >= 0, e

    @isolate
    def test_pre_check_inputs(self):
        """Should fail if don't nowk where to download """
        project = " <- http://www.google.com/ ! download"
        pp = ProjectParser()
        pp.set_project(project)
        try:
            workflow = pp.parse_extend_and_check_project()
            assert False, "An exception should be raised"
        except TuttleError as e:
            assert e.message.find("don't know how to handle these outputs") >= 0, e.message

    @isolate
    def test_simple_dl(self):
        """ Should download a simple url to a file """
        project = """file://huge_resource.js <- http://localhost:8043/huge_resource.js ! download"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert isfile('huge_resource.js')

    @isolate
    def test_can_download_in_sub_dir(self):
        """ Should download as long as there is one file output and exactly one downloadable resource """
        sleep(0.5) # Travis needs some time before running the project or http mock server won't be available
        project = """file://a_directory/a_resource <- http://localhost:8043/a_resource file://a_directory ! download

file://a_directory <-
        mkdir a_directory
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert isdir('a_directory')
        assert isfile('a_directory/a_resource')

    # @isolate
    # def test_download_fails(self):
    #     """Should raise an exception if download fails"""
    #     project = " file://tuttle.html <- http://www.example.com/tuttle ! download"
    #     pp = ProjectParser()
    #     pp.set_project(project)
    #     # Don't check project or execution of the workflow will not be allowed because input resource is missing
    #     workflow = pp.parse_project()
    #     print workflow._processes
    #     print [res.url for res in workflow._processes[0].inputs]
    #     workflow.prepare_execution()
    #     workflow.run()
    #     assert isfile("tuttle.html")

    @isolate
    def test_pre_check_before_running(self):
        """ Pre check should happen for each process before run the whole workflow """
        project = """file://A <-
        obvious failure
file://google.html <- file://A ! download
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2
        assert output.find("Download processor") >= 0, output

    @isolate
    def test_no_error_with_download_process(self):
        """ Download process does not create code in reserved_path for the process... Thus it cant be moved when """
        """ retreiving logs and reserved path from previous execution(from bug) """
        project = """file://g <-  http://localhost:8043/a_resource ! download

file://h <- file://g
    ERROR
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2, output
        rcode, output = tuttle_invalidate()
        assert rcode == 0, output
        rcode, output = run_tuttle_file()
        assert rcode == 2, output

    @isolate
    def test_pre_check_before_invalidation(self):
        """Pre check should happen before invalidation"""
        project1 = """file://A <-
        echo A > A
        """
        rcode, output = run_tuttle_file(project1)
        assert isfile('A')
        project2 = """file://A <-
        echo different > A
file://google.html <- file://A ! download
        """
        rcode, output = run_tuttle_file(project2)
        assert rcode == 2
        assert output.find("* file://B") == -1
        assert output.find("Download processor") >= 0, output

    @isolate
    def test_download_https(self):
        """ https download should work """
        if not online:
            raise SkipTest("Offline")
        project = "file://google.html <- https://www.google.com/ ! download"
        rcode, output = run_tuttle_file(project)

        if output.find("SSL certificate problem: unable to get local issuer certificate") >= 0:
            raise SkipTest("Skip test because of a certificate bug from appveyor")

        assert rcode == 0, output
        assert isfile("google.html")
        content = open("google.html").read()
        assert content.find("<title>Google</title>") >= 0
        logs = open(join(".tuttle", "processes", "logs", "tuttlefile_1_stdout.txt"), "r").read()
        assert re.search("\n\.+\n", logs) is not None, logs
        assert isfile(join(".tuttle", "processes", "logs", "tuttlefile_1_err.txt"))

    def run_ftp_server(self):
        authorizer = DummyAuthorizer()
        ftp_dir = join(dirname(__file__), 'ftp')
        authorizer.add_user("user", "password", ftp_dir, perm="elrd")
        handler = FTPHandler
        handler.authorizer = authorizer
        self._ftpd = FTPServer(("0.0.0.0", 8021), handler)
        self._ftpd.serve_forever(timeout=0.2, handle_exit=True)

    @isolate
    def test_download_ftp_resource(self):
        """Download processor should be able to download an ftp resource with authentification """
        from threading import Thread
        p = Thread(target=self.run_ftp_server)
        p.start()
        try:
            sleep(0.1)  # The server needs time to start

            project = """file://downloaded_resource <- ftp://localhost:8021/ftp_resource ! download
            """
            passfile = join(dirname(__file__), '.tuttlepass')
            with EnvVar('TUTTLEPASSFILE', passfile):
                rcode, output = run_tuttle_file(project)
            assert rcode == 0, output
            assert isfile('downloaded_resource')
        finally:
            self._ftpd.close_all()
            self._ftpd.ioloop.close()
            p.join()
