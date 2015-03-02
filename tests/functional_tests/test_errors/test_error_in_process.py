# -*- coding: utf-8 -*-
import glob

from subprocess import CalledProcessError
from sys import stderr
from os import getcwd
from tests.functional_tests import FunctionalTestBase, isolate


class TestErrorInProcess(FunctionalTestBase):

    @isolate(['A'])
    def test_error_in_process(self):
        """  When a process fail, Tuttle should exit with status code 2"""
        # As in Gnu Make
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

    @isolate(['A', 'test_error_in_process.py'])
    def test_isolation_decorator(self):
        files = glob.glob("*")
        assert files == ['A', 'test_error_in_process.py']

    @isolate
    def test_isolation_decorator_without_args(self):
        assert True