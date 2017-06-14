# -*- coding: utf-8 -*-

from tests.functional_tests import isolate, run_tuttle_file
from cStringIO import StringIO
from tuttle.workflow_runner import get_logger
from tuttle.log_follower import LogTracer
import logging
import sys


class CaptureOutputs(object):
    """
    Captures stdin and stdout
    """
    def __init__(self):
        self._oldout, self._olderr = sys.stdout, sys.stderr

    def __enter__(self):
        self._out = StringIO()
        sys.stdout,sys.stderr = self._out, self._out
 
    def __exit__(self, *args):
        sys.stdout, sys.stderr = self._oldout, self._olderr
        self.output = self._out.getvalue()


class TestLogFollower():
    
    @isolate([])
    def test_log_single_file(self):
        """LogTracer logs the content of a file in stdout"""
        oldout, olderr = sys.stdout, sys.stderr
        out = StringIO()
        try:
            sys.stdout,sys.stderr = out, out
            logger = get_logger()
            lt = LogTracer(logger, logging.INFO, "test.log")
            with open("test.log", "w") as f:
                f.write("line 1\n")
                f.write("line 2\n")
                f.write("line 3\n")
            lt.trace()
        finally:
            sys.stdout, sys.stderr = oldout, olderr
        output = out.getvalue()
        assert output.find("line 1") >= 0, output
        assert output.find("line 2") >= 0, output
        assert output.find("line 3") >= 0, output
