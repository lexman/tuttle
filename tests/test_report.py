# -*- coding: utf-8 -*-
from os.path import isfile, join
from re import search, DOTALL, findall

from tests.functional_tests import isolate, run_tuttle_file


class TestReport:

    @isolate(['A'])
    def test_success(self):
        """ If a workflow finishes with all processes in success, it should display success in the main title"""
        project = """file://B <- file://A
    echo A produces B
    echo B > B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0
        report_path = join('.tuttle', 'report.html')
        assert isfile(report_path)
        report = open(report_path).read()
        title_match = search(r'<h1>.*Success.*</h1>', report, DOTALL)
        assert title_match, report
        title_2_match = search(r'<h2.*Success.*</h2>', report, DOTALL)
        assert title_2_match, report

    @isolate(['A'])
    def test_failure(self):
        """ If process in the workflow fails, the report should display failure in the main title"""
        project = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    echo B produces C
    echo B produces C > C
    failure on purpose
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 2
        report_path = join('.tuttle', 'report.html')
        assert isfile(report_path)
        report = open(report_path).read()
        title_match = search(r'<h1>.*Failure.*</h1>', report, DOTALL)
        assert title_match, report
        title_2_match = search(r'<h2.*Failure.*</h2>', report, DOTALL)
        assert title_2_match, report

    @isolate(['A'])
    def test_a_failure_in_a_process_without_output_should_be_marked_in_the_repoort(self):
        """ If process without outputs fails, the report should display failure in the main title"""
        project = """<- file://A
    failure on purpose
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 2
        report_path = join('.tuttle', 'report.html')
        assert isfile(report_path)
        report = open(report_path).read()
        title_match = search(r'<h1>.*Failure.*</h1>', report, DOTALL)
        assert title_match, report
        title_2_match = search(r'<h2.*Failure.*</h2>', report, DOTALL)
        assert title_2_match, report

    @isolate(['A'])
    def test_all_relative_links_must_exists(self):
        """ If process without outputs fails, the report should display failure in the main title"""
        project = """file://B <- file://A
    echo A produces B > B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0
        report_path = join('.tuttle', 'report.html')
        assert isfile(report_path)
        report = open(report_path).read()
        links = findall(r'<a href=\"([^"]*)>', report)
        for link in links:
            rel_path = link[1].split('/')
            path = join('.tuttle', *rel_path)
            assert isfile(path), path

    @isolate(['A'])
    def test_all_imports_must_exists(self):
        """ If process without outputs fails, the report should display failure in the main title"""
        project = """file://B <- file://A
    echo A produces B > B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0
        report_path = join('.tuttle', 'report.html')
        assert isfile(report_path)
        report = open(report_path).read()
        links = findall(r'src=\"([^"]*)>', report)
        for link in links:
            rel_path = link[1].split('/')
            path = join('.tuttle', *rel_path)
            assert isfile(path), path
