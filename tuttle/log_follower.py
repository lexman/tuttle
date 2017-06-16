# -*- coding: utf8 -*-

"""
Utility methods for to send processes logs to a python logger.
"""


import logging
import sys
from os.path import isfile
from time import sleep
from threading import Thread


class LogTracer:
        
    READ_SIZE = 1024
    TUTTLE = 22
    STDOUT = 24
    STDERR = 26
    
    def __init__(self, logger, loglevel, filename):
        self._filename = filename
        self._logger = logger
        self._loglevel = loglevel
        self._filedescr = None
        
    def trace(self):
        if not self._filedescr:
            if isfile(self._filename):
                self._filedescr = open(self._filename, 'r')
        traced = False
        if self._filedescr:
            lines = self._filedescr.readlines(self.READ_SIZE)
            for line in lines:
                traced = True
                if line[-1:] == "\n":
                    self._logger.log(self._loglevel, line[:-1])
                else:
                    self._logger.log(self._loglevel, line)
        return traced

    @staticmethod
    def get_logger():
        logger = logging.getLogger(__name__)
        logging.addLevelName(LogTracer.TUTTLE, 'tuttle')
        logging.addLevelName(LogTracer.STDOUT, 'stdout')
        logging.addLevelName(LogTracer.STDERR, 'stderr')
        formater = logging.Formatter("[%(levelname)s] %(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formater)
        handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        return logger


class LogsFollower:
    
    def __init__(self):
        self._logs = []
        self._stop = False
        
    def add_log(self, logger, filestdout, filestderr):
        tracer_stdin = LogTracer(logger, LogTracer.STDOUT, filestdout)
        tracer_stderr = LogTracer(logger, LogTracer.STDERR, filestderr)
        self._logs.append(tracer_stdin)
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
            traced = True
            while True:
                traced = self.trace_logs()
                if self._stop and not traced:
                    break
                if not traced:
                    sleep(0.1)
        self._thread = Thread(target=trace_logs_until_stop, name="worker")
        self._thread.start()
        print(self._thread.is_alive())
        
    def stop(self):
        #sleep(0.1) # wait for flush
        self._stop = True
        self._thread.join()

    @staticmethod
    def get_logger():
        return LogTracer.get_logger()
                
