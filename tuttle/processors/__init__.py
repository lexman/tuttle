#!/usr/bin/env python
# -*- coding: utf8 -*-

from os import path, chmod, stat
from stat import S_IXUSR, S_IXGRP, S_IXOTH
from subprocess import Popen, PIPE

def run_and_log(prog, log_stdout, log_stderr):
    fout = open(log_stdout, 'w')
    ferr = open(log_stderr, 'w')
    osprocess = Popen([prog], stdout=fout.fileno(), stderr=ferr.fileno())
    fout.close()
    ferr.close()
    rcode = osprocess.wait()
    return rcode


class ShellProcessor:
    """ A processor to run *nix shell code
    """
    name = 'shell'
    header = "#!/usr/bin/env sh\n"

    def generate_executable(self, code, line_num, directory):
        """ Create an executable file
        :param directory: string
        :return: the path to the file
        """
        script_name = path.join(directory, "shell_{}".format(line_num))
        with open(script_name, "w+") as f:
            f.write(self.header)
            f.write(code)
        mode = stat(script_name).st_mode
        chmod(script_name, mode | S_IXUSR | S_IXGRP | S_IXOTH)
        return script_name

    def run(self, script_path, logs_dir):
        script_name = path.basename(script_path)
        print "=" * 60
        print script_name
        print "=" * 60
        prog = path.abspath(script_path)
        log_stdout = path.join(logs_dir, "{}_stdout".format(script_name))
        log_stderr = path.join(logs_dir, "{}_err".format(script_name))
        ret_code = run_and_log(prog, log_stdout, log_stderr)
        f = open(log_stdout, "r")
        print f.read()
        f.close()
        print "-" * 60
        f = open(log_stderr, "r")
        print f.read()
        f.close()
        if ret_code:
            print "-" * 60
            print("Process {} failed".format(script_name))


class BatProcessor:
    """ A processor for Windows command line
    """
    name = 'bat'
    header = "@echo off\n"

    def generate_executable(self, code, line_num, directory):
        """ Create an executable file
        :param directory: string
        :return: the path to the file
        """
        script_name = path.join(directory, "shell_{}.bat".format(line_num))
        with open(script_name, "w+") as f:
            f.write(self.header)
            f.write(code)
        return script_name

    def run(self, script_path, logs_dir):
        script_name = path.basename(script_path)
        print "=" * 60
        print script_name
        print "=" * 60
        print "--- stdout : ", "-" * 47
        prog = path.abspath(script_path)
        log_stdout = path.join(logs_dir, "{}_stdout".format(script_name))
        log_stderr = path.join(logs_dir, "{}_err".format(script_name))
        ret_code = run_and_log(prog, log_stdout, log_stderr)
        f = open(log_stdout, "r")
        print f.read()
        f.close()
        print "--- stderr : ", "-" * 47
        f = open(log_stderr, "r")
        print f.read()
        f.close()
        if ret_code:
            print "-" * 60
            print
            print("Process {} failed with return code {}".format(script_name, ret_code))

