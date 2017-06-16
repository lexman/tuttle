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
    def test_log_should_not_double_carriage_return(self):
        """ """
        with CaptureOutputs() as co:
            logger = get_logger()
            lt = LogTracer(logger, logging.INFO, "test.log")
            with open("test.log", "w") as f:
                f.write("line 1\n")
                f.write("line 2\n")
            lt.trace()
        output = co.output
        assert output.find("\n\n") == -1, output

    @isolate([])
    def test_log_should_(self):
        """ The last char of the file must be logged even if the 
            file does not finish with CR """
        with CaptureOutputs() as co:
            logger = get_logger()
            lt = LogTracer(logger, logging.INFO, "test.log")
            with open("test.log", "w") as f:
                f.write("line 1")
            lt.trace()
        output = co.output
        assert output.find("line 1") >= 0, output

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

    @isolate([])
    def test_log_format(self):
        """logs should display log level and message"""
        with CaptureOutputs() as co:
            logger = LogTracer.get_logger()
            logger.info("MESSAGE")
        assert co.output.find("[INFO] MESSAGE") == 0, co.output
        
    @isolate([])
    def test_log_format_stdout_stderr(self):
        """logs should display log level and message"""
        with CaptureOutputs() as co:
            logger = LogTracer.get_logger()
            lf = LogsFollower()
            lf.add_log(logger, "stdout", "stderr")
            with open("stdout", "w") as fout, \
                 open("stderr", "w") as ferr:
                     fout.write("file stdout")
                     ferr.write("file stderr")
            while lf.trace_logs():
                pass
            
        assert co.output.find("[stdout] file stdout") >= 0, co.output
        assert co.output.find("[stderr] file stderr") >= 0, co.output        

    @isolate([])
    def test_log_in_background(self):
        """Should log in background ans stop when foreground processing 
           is over"""
        import time
        with CaptureOutputs() as co:
            logger = LogTracer.get_logger()
            lf = LogsFollower()
            lf.add_log(logger, "stdout", "stderr")
            lf.trace_in_background()
            with open("stdout", "w") as fout, \
                 open("stderr", "w") as ferr:
                     fout.write("file stdout")
                     ferr.write("file stderr")
            lf.stop()
        assert co.output.find("[stdout] file stdout") >= 0, co.output
        assert co.output.find("[stderr] file stderr") >= 0, co.output        


    @isolate([])
    def test_log_a_lot_in_background(self):
        """Should log in background ans stop when foreground processing 
           is over even with a lot a data"""
        import time
        with CaptureOutputs() as co:
            logger = LogTracer.get_logger()
            lf = LogsFollower()
            lf.add_log(logger, "stdout", "stderr")
            lf.trace_in_background()
            with open("stdout", "w") as fout, \
                 open("stderr", "w") as ferr:
                     fout.write("file stdout")
                     ferr.write("file stderr")
                     for i in xrange(5000):
                        fout.write("stdout - line {}\n".format(i))
                        ferr.write("stderr - line {}\n".format(i))
            lf.stop()
        assert co.output.find("[stdout] stdout - line 1") >= 0, co.output
        assert co.output.find("[stderr] stderr - line 1") >= 0, co.output        
        assert co.output.find("[stdout] stdout - line 4999") >= 0, co.output
        assert co.output.find("[stderr] stderr - line 4999") >= 0, co.output        
