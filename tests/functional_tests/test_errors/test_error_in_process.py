# -*- coding: utf-8 -*-

import glob
from tests.functional_tests import isolate, run_tuttle_file


class TestErrorInProcess():

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
        rcode, output = run_tuttle_file(first)
        assert rcode == 2

    @isolate(['A', 'test_error_in_process.py'])
    def test_isolation_decorator(self):
        files = glob.glob("*")
        assert files == ['A', 'test_error_in_process.py']

    @isolate
    def test_isolation_decorator_without_args(self):
        assert True

    @isolate(['A'])
    def test_fail_if_already_failed(self):
        """  When a process fail, Tuttle should exit with status code 2"""
        # As in Gnu Make
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    error
    echo This should not be written
    echo C > C

file://D <- file://A
    echo A produces D
    echo D > D
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 2

        second = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    error
    echo This should not be written
    echo C > C

file://D <- file://A
    echo A produces D
    echo Minor change
    echo D > D
"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 2
        assert output.find("Workflow already failed") >= 0
