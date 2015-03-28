# -*- coding: utf-8 -*-
import glob

from subprocess import CalledProcessError, Popen, PIPE
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
        rcode, output = self.run_tuttle()
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
        self.write_tuttlefile(first)
        rcode, output = self.run_tuttle()
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
        self.write_tuttlefile(second)
        proc = Popen(['python', self._tuttle_cmd], stdout=PIPE)
        result = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2
        assert result.find("Workflow already failed") >= 0
