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


def print_log(log_file, header):
    with open(log_file, "r") as f:
        content = f.read()
        if len(content) > 1 :
            print "--- {} : {}".format(header, "-" * (60 - len(header)))
            print content


class ShellProcessor:
    """ A processor to run *nix shell code
    """
    name = 'shell'
    header = "#!/usr/bin/env sh\n"

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

    def run(self, script_path, process_id, logs_dir):
        script_name = path.basename(script_path)
        print "=" * 60
        print script_name
        print "=" * 60
        log_stdout = path.join(logs_dir, "{}_stdout".format(process_id))
        log_stderr = path.join(logs_dir, "{}_err".format(process_id))
        prog = path.abspath(script_path)
        ret_code = run_and_log(prog, log_stdout, log_stderr)
        log_stdout = path.join(logs_dir, "{}_stdout".format(process_id))
        log_stderr = path.join(logs_dir, "{}_err".format(process_id))
        if ret_code:
            print "-" * 60
            print("Process {} failed".format(script_name))


class BatProcessor:
    """ A processor for Windows command line
    """
    name = 'bat'
    header = "@echo off\n"

    def generate_executable(self, code, process_id, directory):
        """ Create an executable file
        :param directory: string
        :return: the path to the file
        """
        script_name = path.join(directory, "{}.bat".format(process_id))
        with open(script_name, "w+") as f:
            f.write(self.header)
            f.write(code)
        return script_name

    def run(self, script_path, process_id, logs_dir):
        print "=" * 60
        print process_id
        print "=" * 60
        prog = path.abspath(script_path)
        log_stdout = path.join(logs_dir, "{}_stdout".format(process_id))
        log_stderr = path.join(logs_dir, "{}_err".format(process_id))
        ret_code = run_and_log(prog, log_stdout, log_stderr)
        print_log(log_stdout, "stdout")
        print_log(log_stderr, "stderr")
        if ret_code:
            print "-" * 60
            print
            print("Process {} failed with return code {}".format(process_id, ret_code))

