# -*- coding: utf-8 -*-

from tests.functional_tests import isolate, run_tuttle_file
from cStringIO import StringIO
from tuttle.workflow_runner import get_logger
from tuttle.log_follower import LogTracer, LogsFollower
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
        return self
 
    def __exit__(self, *args):
        sys.stdout, sys.stderr = self._oldout, self._olderr
        self.output = self._out.getvalue()


class TestLogFollower():
    
    @isolate([])
    def test_log_single_file(self):
        """LogTracer should log the content of a file"""
        with CaptureOutputs() as co:
            logger = get_logger()
            lt = LogTracer(logger, logging.INFO, "test.log")
            with open("test.log", "w") as f:
                f.write("line 1\n")
                f.write("line 2\n")
                f.write("line 3\n")
            lt.trace()
        output = co.output
        assert output.find("line 1") >= 0, output
        assert output.find("line 2") >= 0, output
        assert output.find("line 3") >= 0, output

    @isolate([])
    def test_log_huge_file(self):
        """LogTracer should log the content of a big file in stdout"""
        with CaptureOutputs() as co:
            logger = get_logger()
            lt = LogTracer(logger, logging.INFO, "test.log")
            with open("test.log", "w") as f:
                for i in xrange(5000):
                    f.write("line {}\n".format(i))
            while lt.trace():
                pass
        output = co.output
        assert output.find("line 1") >= 0, output
        assert output.find("line 2") >= 0, output
        assert output.find("line 3") >= 0, output
        assert output.find("line 4999") >= 0, output

    @isolate([])
    def test_log_multiple_files(self):
        """LogTracer should log the content of several files in stdout"""
        with CaptureOutputs() as co:
            logger = get_logger()
            lf = LogsFollower()
            lf.add_log(logger, "w1.stdout", "w1.stderr")
            lf.add_log(logger, "w2.stdout", "w2.stderr")
            lf.add_log(logger, "w3.stdout", "w3.stderr")

            with open("w1.stdout", "w") as fo1, \
                 open("w1.stderr", "w") as fe1, \
                 open("w2.stdout", "w") as fo2, \
                 open("w2.stderr", "w") as fe2, \
                 open("w3.stdout", "w") as fo3, \
                 open("w3.stderr", "w") as fe3 :
                     
                for i in xrange(5000):
                    fo1.write("w1.stdout - line {}\n".format(i))
                    fe1.write("w1.stderr - line {}\n".format(i))
                    fo2.write("w2.stdout - line {}\n".format(i))
                    fe2.write("w2.stderr - line {}\n".format(i))
                    fo3.write("w3.stdout - line {}\n".format(i))
                    fe3.write("w3.stderr - line {}\n".format(i))

            while lf.trace_logs():
                pass
        output = co.output
        assert output.find("w1.stderr - line 1") >= 0, output
        assert output.find("w1.stdout - line 1") >= 0, output
        assert output.find("w2.stderr - line 1") >= 0, output
        assert output.find("w2.stdout - line 1") >= 0, output
        assert output.find("w3.stdout - line 1") >= 0, output
        assert output.find("w3.stderr - line 1") >= 0, output

        assert output.find("w1.stderr - line 4999") >= 0, output
        assert output.find("w1.stdout - line 4999") >= 0, output
        assert output.find("w2.stderr - line 4999") >= 0, output
        assert output.find("w2.stdout - line 4999") >= 0, output
        assert output.find("w3.stdout - line 4999") >= 0, output
        assert output.find("w3.stderr - line 4999") >= 0, output
