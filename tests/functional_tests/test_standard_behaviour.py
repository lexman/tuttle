# -*- coding: utf-8 -*-
from os.path import isfile, join

from os import path
from tests.functional_tests import isolate, run_tuttle_file


class TestStandardBehaviour:

    @isolate(['A'])
    def test_create_resource(self):
        """ When launching "tuttle" in the command line, should produce the result"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

"""
        rcode, output = run_tuttle_file(first)
        assert path.exists('B')

    @isolate(['A'])
    def test_create_report(self):
        """ When launching "tuttle" in the command line, should produce the result"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

"""
        rcode, output = run_tuttle_file(first)
        assert path.exists('tuttle_report.html')

    @isolate(['A'])
    def test_report_execution(self):
        """ When launching "tuttle" in the command line, should produce the html report"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    error
    echo B produces C
    echo C > C

file://D <- file://C
    echo C produces D
    echo D > D
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 2
        assert isfile('tuttle_report.html')
        assert path.isfile(path.join(".tuttle", "last_workflow.pickle"))
        second = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    another error
    echo B produces C
    echo C > C

file://D <- file://C
    echo C produces D
    error
    echo D > D
"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 2
        report = file('tuttle_report.html').read()
        [_, sec1, sec2, sec3] = report.split('<h2')
        assert sec1.find("<th>Start</th>") >= 0, sec1
        assert sec2.find("<th>Start</th>") >= 0, sec2
        assert sec3.find("<th>Start</th>") == -1, sec3

    @isolate(['A'])
    def test_workflow_execution_should_stop_at_first_process_error(self):
        """ Should invalidate a resource if the code creating it changes
        """
        project = """file://B <- file://A
        echo A produces B > B
        error

file://C <- file://B
        echo B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        assert not path.exists('C')

    @isolate(['A'])
    def test_should_tell_if_already_ok(self):
        """ If nothing has to run, the user should be informed every thing is ok
        """
        project = """file://B <- file://A
        echo A produces B > B
        echo A produces B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("A produces B") >= 0
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("Everything up to date") >= 0, output
