# -*- coding: utf8 -*-
from shutil import copyfileobj
from urllib2 import Request, urlopen

from os import path, chmod, stat, mkdir
from stat import S_IXUSR, S_IXGRP, S_IXOTH
from subprocess import Popen, PIPE
from tuttle.error import TuttleError


class ProcessExecutionError(TuttleError):
    pass


def run_and_log(prog, log_stdout, log_stderr):
    fout = open(log_stdout, 'w')
    ferr = open(log_stderr, 'w')
    osprocess = Popen([prog], stdout=fout.fileno(), stderr=ferr.fileno(), stdin=PIPE)
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
    header = "#!/usr/bin/env sh\nset -e\nset -x\n"

    def generate_executable(self, process, script_path):
        """ Create an executable file
        :param directory: string
        :return: the path to the file
        """
        with open(script_path, "w+") as f:
            f.write(self.header)
            f.write(process._code)
        mode = stat(script_path).st_mode
        chmod(script_path, mode | S_IXUSR | S_IXGRP | S_IXOTH)

    def run(self, process, reserved_path, log_stdout, log_stderr):
        self.generate_executable(process, reserved_path)
        run_and_log(reserved_path, log_stdout, log_stderr)

    def pre_check(self, process):
        pass


class BatProcessor:
    """ A processor for Windows command line
    """
    name = 'bat'
    header = "@echo off\n"
    exit_if_fail = 'if %ERRORLEVEL% neq 0 exit /b 1\n'

    def generate_executable(self, process, reserved_path):
        """ Create an executable file
        :param directory: string
        :return: the path to the file
        """
        mkdir(reserved_path)
        script_name = path.abspath(path.join(reserved_path, "{}.bat".format(process.id)))
        with open(script_name, "w+") as f:
            f.write(self.header)
            lines = process._code.split("\n")
            for line in lines:
                f.write(line)
                f.write("\n")
                f.write(self.exit_if_fail)
        return script_name

    def run(self, process, reserved_path, log_stdout, log_stderr):
        prog = self.generate_executable(process, reserved_path)
        run_and_log(prog, log_stdout, log_stderr)

    def pre_check(self, process):
        pass


class DownloadProcessor:
    """ A processor for downloading http resources
    """
    name = 'download'
    user_agent = 'tuttle'

    def pre_check(self, process):
        inputs = [res for res in process.iter_inputs()]
        outputs = [res for res in process.iter_outputs()]
        if len(inputs) != 1 \
           or len(outputs) != 1 \
           or inputs[0].scheme != 'http' \
           or outputs[0].scheme != 'file':
            raise TuttleError("Download processor {} don't know how to handle his inputs / outputs".format(process.id))

    def run(self, process, reserved_path, log_stdout, log_stderr):
        # TODO how do we handle errors ?
        inputs = [res for res in process.iter_inputs()]
        outputs = [res for res in process.iter_outputs()]
        file_name = outputs[0]._path
        url = inputs[0].url
        headers = {"User-Agent" : self.user_agent}
        req = Request(url, headers = headers)
        fin = urlopen(req)
        with open(file_name, 'wb') as fout:
            copyfileobj(fin, fout)
        return 0
