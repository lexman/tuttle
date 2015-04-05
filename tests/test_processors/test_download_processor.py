# -*- coding: utf8 -*-
from os.path import isfile

from tests.functional_tests import isolate, FunctionalTestBase
from tuttle.project_parser import ProjectParser


class TestDownloadProcessor(FunctionalTestBase):

    @isolate
    def test_standard_download(self):
        """Should download a simple url"""
        project = " file://google.html <- http://www.google.com/ #! download"
        pp = ProjectParser()
        pp.set_project(project)
        workflow = pp.parse_and_check_project()
        workflow.prepare_execution()
        workflow.run()
        assert isfile("google.html")
        content = open("google.html").read()
        assert content.find("<title>Google</title>") >= 0

    @isolate
    def test_pre_check(self):
        """Should fail if not http:// <- file:// """
        project = " http://www.google.com/ <-  #! download"
        pp = ProjectParser()
        pp.set_project(project)
        workflow = pp.parse_and_check_project()
        try:
            workflow.prepare_execution()
            assert False, "An exception should be raised"
        except:
            assert True


    # @isolate
    # def test_download_fails(self):
    #     """Should raise an exception if download fails"""
    #     project = " file://tuttle.html <- http://www.example.com/tuttle #! download"
    #     pp = ProjectParser()
    #     pp.set_project(project)
    #     # Don't check project or execution of the workflow will not be allowed because input resource is missing
    #     workflow = pp.parse_project()
    #     print workflow.processes
    #     print [res.url for res in workflow.processes[0].inputs]
    #     workflow.prepare_execution()
    #     workflow.run()
    #     assert isfile("tuttle.html")

    @isolate
    def test_pre_check_works_before_running(self):
        """Should download a simple url"""
        project = """file://A <-
        obvious failure

file://google.html <- file://A, http://www.google.com/ #! download
        """
        self.write_tuttlefile(project)
        rcode, output = self.run_tuttle()
        assert rcode == 2
        assert output.find("Download processor") >= 0, output
