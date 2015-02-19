# -*- coding: utf-8 -*-

from os import path
from tests.functional_tests import FunctionalTestBase


class TestStandardBehaviour(FunctionalTestBase):

    def test_create_resource(self):
        """ When launching "tuttle" in the command line, should produce the result"""
        self.work_dir_from_module(__file__)
        first = """file://B <- file://A
    echo A produces B
    echo B > B

"""
        self.write_tuttlefile(first)
        result = self.run_tuttle()
        assert path.exists('B')
        self._rm('B')

    def test_create_report(self):
        """ When launching "tuttle" in the command line, should produce the result"""
        self.work_dir_from_module(__file__)
        first = """file://B <- file://A
    echo A produces B
    echo B > B

"""
        self.write_tuttlefile(first)
        result = self.run_tuttle()
        assert path.exists('tuttle_report.html')
        self._rm('B')

