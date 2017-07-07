# -*- coding: utf8 -*-

"""
Utility methods for to send processes logs to a python logger.
"""


import logging
import sys
from os.path import isfile
from time import sleep
from threading import Thread
from traceback import format_exception


class LogTracer:
        
    READ_SIZE = 1024

    def __init__(self, logger, namespace, filename):
        self._filename = filename
        self._logger = logger
        self._namespace = namespace
        self._filedescr = None

    @staticmethod
    def remove_ending_cr(line):
        if line[-1:] == "\n":
            return line[:-1]
        else:
            return line

    def trace(self):
        if not self._filedescr:
            if isfile(self._filename):
                self._filedescr = open(self._filename, 'r')
        traced = False
        if self._filedescr:
            lines = self._filedescr.readlines(self.READ_SIZE)
            for line in lines:
                traced = True
                msg = "[{}] {}".format(self._namespace, LogTracer.remove_ending_cr(line))
                self._logger.info(msg)
        return traced

    def close(self):
        if self._filedescr:
            self._filedescr.close()

class EnsureLogsFollowerStops(object):
    """
    Ensures a LogFollower is stopped when no longer required
    """
    def __init__(self, lf):
        self._lf = lf

    def __enter__(self):
        pass
 
    def __exit__(self, *args):
        self._lf.terminate()


class LogsFollower:
    
    def __init__(self):
        self._logs = []
        self._terminate = False
        self._logger = LogsFollower.get_logger()

    def follow_process(self, filestdout, filestderr, process_name):
        """ Adds 2 files to follow : the stderr and stdin of a process """
        tracer_stdout = LogTracer(self._logger, "{}::stdout".format(process_name), filestdout)
        tracer_stderr = LogTracer(self._logger, "{}::stderr".format(process_name), filestderr)
        self._logs.append(tracer_stdout)
        self._logs.append(tracer_stderr)
        
    def trace_logs(self):
        traced = False
        for log in self._logs:
            if log.trace():
                traced = True
        return traced
            
    def trace_logs_forever(self):
        while True:
            if not self.trace_logs():
                sleep(0.1)

    def trace_in_background(self):
        def trace_logs_until_stop():
            while True:
                traced = self.trace_logs()
                if self._terminate and not traced:
                    break
                if not traced:
                    sleep(0.1)
        self._thread = Thread(target=trace_logs_until_stop, name="worker")
        self._thread.start()
        return EnsureLogsFollowerStops(self)
        
    def terminate(self):
        #sleep(0.1) # wait for flush
        self._terminate = True
        self._thread.join()
        for log in self._logs:
            log.close()

    @staticmethod
    def get_logger():
        logger = logging.getLogger(__name__)
        formater = logging.Formatter("%(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formater)
        handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        return logger
