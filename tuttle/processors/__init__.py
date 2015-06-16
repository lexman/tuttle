# -*- coding: utf8 -*-

from os import path, chmod, stat, mkdir
from stat import S_IXUSR, S_IXGRP, S_IXOTH
from subprocess import Popen, PIPE
from tuttle.error import TuttleError


class ProcessExecutionError(TuttleError):
    pass


def run_and_log(args, log_stdout, log_stderr):
    fout = open(log_stdout, 'w')
    ferr = open(log_stderr, 'w')
    osprocess = Popen(args, stdout=fout.fileno(), stderr=ferr.fileno(), stdin=PIPE)
    osprocess.stdin.close()
    fout.close()
    ferr.close()
    rcode = osprocess.wait()
    if rcode != 0:
        msg = "Process ended with error code {}".format(rcode)
        raise ProcessExecutionError(msg)


class ShellProcessor:
    """ A processor to run *nix shell code
    """
    name = 'shell'
    header = u"#!/usr/bin/env sh\nset -e\nset -x\n"

    def generate_executable(self, process, script_path):
        """ Create an executable file
        :param directory: string
        :return: the path to the file
        """
        with open(script_path, "wb+") as f:
            f.write(self.header)
            f.write(process._code.encode('utf8'))
        mode = stat(script_path).st_mode
        chmod(script_path, mode | S_IXUSR | S_IXGRP | S_IXOTH)

    def run(self, process, reserved_path, log_stdout, log_stderr):
        self.generate_executable(process, reserved_path)
        run_and_log([reserved_path], log_stdout, log_stderr)

    def static_check(self, process):
        pass


class BatProcessor:
    """ A processor for Windows command line
    """
    name = 'bat'
    header = u"@echo off\n"
    exit_if_fail = u'if %ERRORLEVEL% neq 0 exit /b 1\n'

    def generate_executable(self, process, reserved_path):
        """ Create an executable file
        :param directory: string
        :return: the path to the file
        """
        mkdir(reserved_path)
        script_name = path.abspath(path.join(reserved_path, "{}.bat".format(process.id)))
        with open(script_name, "wb+") as f:
            f.write(self.header)
            lines = process._code.split("\n")
            for line in lines:
                f.write(line.encode('utf8'))
                f.write(u"\n")
                f.write(self.exit_if_fail)
        return script_name

    def run(self, process, reserved_path, log_stdout, log_stderr):
        prog = self.generate_executable(process, reserved_path)
        run_and_log([prog], log_stdout, log_stderr)

    def static_check(self, process):
        pass

