# -*- coding: utf8 -*-

import re
from os.path import isfile, join
from tests.functional_tests import isolate, run_tuttle_file
from tuttle.project_parser import ProjectParser
from tuttle.extensions.net import HTTPResource
from BaseHTTPServer import BaseHTTPRequestHandler
from SocketServer import TCPServer


class MockHTTPHandler(BaseHTTPRequestHandler):
    """ This class is used to mock some HTTP behaviours :
    * Etag
    * Last-Modified
    * Neither
    Useful both for running tests offline and for not depending on some external change
    """

    def do_GET(self):
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



class TestHttpResource():

    httpd = None
    p = None

    @classmethod
    def run_server(cls):
        cls.httpd = TCPServer(("", 8042), MockHTTPHandler)
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
        res = HTTPResource("http://www.google.com/")
        assert res.exists()

    def test_fictive_resource_not_exists(self):
        """A fictive resource should not exist"""
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
        assert sig == 'Etag: "359670651+gzip"', sig

    def test_resource_last_modified_signature(self):
        """ An HTTPResource with an Last-Modified should use it as signature in case it doesn't have Etag"""
        #res = HTTPResource("http://www.wikipedia.org/")
        res = HTTPResource("http://localhost:8042/resource_with_last_modified")
        sig = res.signature()
        assert sig == 'Last-Modified: Tue, 30 Jun 1981 03:14:59 GMT', sig

    def test_ressource_signature_without_etag_nor_last_modified(self):
        """ An HTTPResource signature should be a hash of the beginning of the file if we can't rely on headers """
        res = HTTPResource("http://localhost:8042/resource_without_version")
        sig = res.signature()
        assert sig == 'sha1-32K: 7ab4a6c6ca8bbcb3de82530797a0e455070e18fa', sig

class TestHttpsResource():

    def test_real_resource_exists(self):
        """A real resource should exist"""
        res = HTTPResource("https://www.google.com/")
        assert res.exists()

    def test_fictive_resource_not_exists(self):
        """A fictive resource should not exist"""
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


class TestDownloadProcessor():

    @isolate
    def test_standard_download(self):
        """Should download a simple url"""
        project = " file://google.html <- http://www.google.com/ ! download"
        pp = ProjectParser()
        pp.set_project(project)
        workflow = pp.parse_and_check_project()
        workflow.static_check_processes()
        workflow.run()
        assert isfile("google.html")
        content = open("google.html").read()
        assert content.find("<title>Google</title>") >= 0
        logs = open(join(".tuttle", "processes", "logs", "__1_stdout.txt"), "r").read()
        assert re.search("\n\.+\n", logs) is not None
        assert isfile(join(".tuttle", "processes", "logs", "__1_err.txt"))

    @isolate
    def test_long_download(self):
        """ Progress dots should appear in the logs in a long download"""
        project = " file://jquery.js <- http://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js ! download"
        pp = ProjectParser()
        pp.set_project(project)
        workflow = pp.parse_and_check_project()
        workflow.static_check_processes()
        workflow.run()
        assert isfile("jquery.js")
        logs = open(join(".tuttle", "processes", "logs", "__1_stdout.txt"), "r").read()
        assert logs.find("...") >= 0

    @isolate
    def test_pre_check(self):
        """Should fail if not http:// <- file:// """
        project = " http://www.google.com/ <-  ! download"
        pp = ProjectParser()
        pp.set_project(project)
        workflow = pp.parse_and_check_project()
        try:
            workflow.pre_check_processes()
            assert False, "An exception should be raised"
        except:
            assert True


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
        """https download should work"""
        project = "file://google.html <- https://www.google.com/ ! download"
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert isfile("google.html")
        content = open("google.html").read()
        assert content.find("<title>Google</title>") >= 0
        logs = open(join(".tuttle", "processes", "logs", "tuttlefile_1_stdout.txt"), "r").read()
        assert re.search("\n\.+\n", logs) is not None
        assert isfile(join(".tuttle", "processes", "logs", "tuttlefile_1_err.txt"))
