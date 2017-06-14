# -*- coding: utf8 -*-

"""
Utility methods for to send processes logs to a python logger.
"""


import logging
import sys
from os.path import isfile
from time import sleep


class LogTracer:
        
    READ_SIZE = 1024
    
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
                self._logger.info(line[:-1])
        return traced


class LogsFollower:
    
    def __init__(self):
        self._logs = []
        
    def add_log(self, name, filestdout, filestderr):
        tracer_stdin = LogTracer(name, filestdout)
        tracer_stderr = LogTracer(name, filestderr)
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
                
