# -*- coding: utf-8 -*-

from subprocess import CalledProcessError
from tests.functional_tests import FunctionalTestBase

class TestErrorInProcess(FunctionalTestBase):

    def test_error_in_process(self):
        """  When a process fail, Tuttle should exit with status code 2"""
        # As in Gnu Make
        self.work_dir_from_module(__file__)
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    Obvious syntax error
    echo This should not be written
    echo C > C

file://D <- file://A
    echo A produces D
    echo D > D
"""
        self.write_tuttlefile(first)
        try:
            result = self.run_tuttle()
            print result
            assert False
        except CalledProcessError:
            assert True


    def tearDown(self):
        try:
            self.reset()
            self._rm('B')
            self._rm('C')
            self._rm('D')
        finally:
            super(TestErrorInProcess, self).tearDown()