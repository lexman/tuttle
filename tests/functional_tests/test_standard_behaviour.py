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

