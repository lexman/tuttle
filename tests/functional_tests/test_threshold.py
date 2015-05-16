# -*- coding: utf-8 -*-
from os.path import isfile

from os import path
from tests.functional_tests import isolate, run_tuttle_file


class TestThreshold:

    @isolate(['A'])
    def test_abort_if_lost_exceeds_threshold(self):
        """ Should disply a message and abort if processing time lost by invalidation is above the threshold """
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    echo B produces C
    python -c "import time; time.sleep(2)"
    echo C > C
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert isfile('tuttle_report.html')
        assert path.isfile(path.join(".tuttle", "last_workflow.pickle"))
        second = """file://B <- file://A
    echo B has changed
    echo B has changed > B

file://C <- file://B
    echo B produces C
    python -c "import time; time.sleep(2)"
    echo C > C
"""
        rcode, output = run_tuttle_file(second, threshold=1)
        assert rcode == 2, output
        assert output.find("Aborting") >= 0, output

    @isolate(['A'])
    def test_not_abort_if_lost_not_exceeds_threshold(self):
        """ Should disply a message and abort if processing time lost by invalidation is above the threshold """
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    echo B produces C
    echo C > C
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert isfile('tuttle_report.html')
        assert path.isfile(path.join(".tuttle", "last_workflow.pickle"))
        second = """file://B <- file://A
    echo B has changed
    echo B has changed > B

file://C <- file://B
    echo B produces C
    echo C > C
"""
        rcode, output = run_tuttle_file(second, threshold=1)
        assert rcode == 0, output
        assert output.find("Aborting") == -1, output

    @isolate(['A'])
    def test_not_abort_if_threshold_is_0(self):
        """ Should abort if threshold whatever lost time is"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    echo B produces C
    echo C > C
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert isfile('tuttle_report.html')
        assert path.isfile(path.join(".tuttle", "last_workflow.pickle"))
        second = """file://B <- file://A
    echo B has changed
    echo B has changed > B

file://C <- file://B
    echo B produces C
    echo C > C
"""
        rcode, output = run_tuttle_file(second, threshold=0)
        assert rcode == 2, output
        assert output.find("Aborting") >= 0, output
