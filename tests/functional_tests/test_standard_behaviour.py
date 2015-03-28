# -*- coding: utf-8 -*-

from os import path
from tests.functional_tests import FunctionalTestBase, isolate


class TestStandardBehaviour(FunctionalTestBase):

    @isolate(['A'])
    def test_create_resource(self):
        """ When launching "tuttle" in the command line, should produce the result"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

"""
        self.write_tuttlefile(first)
        self.run_tuttle()
        assert path.exists('B')

    @isolate(['A'])
    def test_create_report(self):
        """ When launching "tuttle" in the command line, should produce the result"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

"""
        self.write_tuttlefile(first)
        self.run_tuttle()
        assert path.exists('tuttle_report.html')

    @isolate(['A'])
    def test_report_execution(self):
        """ When launching "tuttle" in the command line, should produce the result"""
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
        self.write_tuttlefile(first)
        rcode, output = self.run_tuttle()
        assert rcode == 2
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
        self.write_tuttlefile(second)
        rcode, output = self.run_tuttle()
        assert rcode == 2
        report = file('tuttle_report.html').read()
        [_, sec1, sec2, sec3] = report.split('<h2>')
        assert sec1.find("<th>Start</th>") >= 0
        assert sec2.find("<th>Start</th>") >= 0
        assert sec3.find("<th>Start</th>") == -1

