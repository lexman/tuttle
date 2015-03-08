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
        result = self.run_tuttle()
        assert path.exists('B')

    @isolate(['A'])
    def test_create_report(self):
        """ When launching "tuttle" in the command line, should produce the result"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

"""
        self.write_tuttlefile(first)
        result = self.run_tuttle()
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
        try:
            result = self.run_tuttle()
            assert False
        except:
            pass
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
        try:
            result = self.run_tuttle()
            assert False
        except:
            pass

        report = file('tuttle_report.html').read()
        [_, sec1, sec2, sec3] = report.split('<hr/>')
        assert sec1.find("Start : 1") >= 0
        assert sec2.find("Start : 1") >= 0
        assert sec3.find("Start : ") >= 0
        print sec3
        assert sec3.find("Start : None") >= 0

