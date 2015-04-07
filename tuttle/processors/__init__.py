# -*- coding: utf8 -*-
from shutil import copyfileobj
from urllib2 import Request, urlopen

from os import path, chmod, stat
from stat import S_IXUSR, S_IXGRP, S_IXOTH
from subprocess import Popen, PIPE
from tuttle.error import TuttleError


def run_and_log(prog, log_stdout, log_stderr):
    fout = open(log_stdout, 'w')
    ferr = open(log_stderr, 'w')
    osprocess = Popen([prog], stdout=fout.fileno(), stderr=ferr.fileno(), stdin=PIPE)
    osprocess.stdin.close()
    fout.close()
    ferr.close()
    rcode = osprocess.wait()
    return rcode


def print_log_if_exists(log_file, header):
    with open(log_file, "r") as f:
        content = f.read()
        if len(content) > 1:
            print "--- {} : {}".format(header, "-" * (60 - len(header) - 7))
            print content


class ShellProcessor:
    """ A processor to run *nix shell code
    """
    name = 'shell'
    header = "#!/usr/bin/env sh\nset -e\nset -o\n"

    def generate_executable(self, code, process_id, directory):
        """ Create an executable file
        :param directory: string
        :return: the path to the file
        """
        script_path = path.join(directory, process_id)
        with open(script_path, "w+") as f:
            f.write(self.header)
            f.write(code)
        mode = stat(script_path).st_mode
        chmod(script_path, mode | S_IXUSR | S_IXGRP | S_IXOTH)
        return script_path

    def print_header(self, process_id):
        print "=" * 60
        print process_id
        print "=" * 60

    def print_logs(self, log_stdout, log_stderr):
        print_log_if_exists(log_stdout, "stdout")
        print_log_if_exists(log_stderr, "stderr")

    def run(self, process, directory, log_stdout, log_stderr):
        prog = self.generate_executable(process._code, process.id, directory)
        self.print_header(process.id)
        ret_code = run_and_log(prog, log_stdout, log_stderr)
        self.print_logs(log_stdout, log_stderr)
        if ret_code:
            print "-" * 60
            print("Process {} failed with return code {}".format(process.id, ret_code))
        return ret_code

    def pre_check(self, process):
        pass


class BatProcessor:
    """ A processor for Windows command line
    """
    name = 'bat'
    header = "@echo off\n"
    exit_if_fail = 'if %ERRORLEVEL% neq 0 exit /b 1\n'

    def generate_executable(self, code, process_id, directory):
        """ Create an executable file
        :param directory: string
        :return: the path to the file
        """
        script_name = path.abspath(path.join(directory, "{}.bat".format(process_id)))
        with open(script_name, "w+") as f:
            f.write(self.header)
            lines = code.split("\n")
            for line in lines:
                f.write(line)
                f.write("\n")
                f.write(self.exit_if_fail)
        return script_name

    def print_header(self, process_id):
        print "=" * 60
        print process_id
        print "=" * 60

    def print_logs(self, log_stdout, log_stderr):
        print_log_if_exists(log_stdout, "stdout")
        print_log_if_exists(log_stderr, "stderr")

    def run(self, process, directory, log_stdout, log_stderr):
        prog = self.generate_executable(process._code, process.id, directory)
        self.print_header(process.id)
        ret_code = run_and_log(prog, log_stdout, log_stderr)
        self.print_logs(log_stdout, log_stderr)
        if ret_code:
            print "-" * 60
            print
            print("Process {} failed with return code {}".format(process.id, ret_code))
        return ret_code

    def pre_check(self, process):
        pass


class DownloadProcessor:
    """ A processor for downloading http resources
    """
    name = 'download'
    user_agent = 'tuttle'

    def pre_check(self, process):
        if len(process.inputs) != 1 \
           or len(process.outputs) != 1 \
           or process.inputs[0].scheme != 'http' \
           or process.outputs[0].scheme != 'file':
            raise TuttleError("Download processor {} don't know how to handle his inputs / outputs".format(process.id))


    def run(self, process, directory, log_stdout, log_stderr):
        # TODO how do we handle errors ?
        file_name = process.outputs[0]._path
        url = process.inputs[0].url
        headers = {"User-Agent" : self.user_agent}
        req = Request(url, headers = headers)
        fin = urlopen(req)
        with open(file_name, 'wb') as fout:
            copyfileobj(fin, fout)
        return 0
