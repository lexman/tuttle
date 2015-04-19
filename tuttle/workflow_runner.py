# -*- coding: utf8 -*-

"""
Utility methods for use in running workflows.
This module is responsible for the inner structure of the .tuttle directory
"""

from shutil import rmtree
from os import remove, makedirs
from os.path import join, isdir, isfile
from tuttle.error import TuttleError


class ResourceError(TuttleError):
    pass


def tuttle_dir(*args):
    return join(".tuttle", *args)


_processes_dir = tuttle_dir("processes")
_logs_dir = tuttle_dir("processes", 'logs')


def prepare_paths(process):
    log_stdout = join(_logs_dir, "{}_stdout".format(process.id))
    log_stderr = join(_logs_dir, "{}_err".format(process.id))
    reserved_path = join(_processes_dir, process.id)
    if isdir(reserved_path):
        rmtree(reserved_path)
    elif isfile(reserved_path):
        remove(reserved_path)
    return reserved_path, log_stdout, log_stderr


def run_process(process):
    reserved_path, log_stdout, log_stderr = prepare_paths(process)
    process.run(reserved_path, log_stdout, log_stderr)
    for res in process.iter_outputs():
        if not res.exists():
            msg = "After execution of process {} : resource {} should have been created".format(process.id,
                                                                                                res.url)
            raise ResourceError(msg)


def create_tuttle_dirs():
    if not isdir(_processes_dir):
        makedirs(_processes_dir)
    if not isdir(_logs_dir):
        makedirs(_logs_dir)


def print_header(process):
    print "=" * 60
    print process.id
    print "=" * 60


def print_log_if_exists(log_file, header):
    if not isfile(log_file):
        return
    with open(log_file, "r") as f:
        content = f.read()
        if len(content) > 1:
            print "--- {} : {}".format(header, "-" * (60 - len(header) - 7))
            print content


def print_logs(process):
    print_log_if_exists(process.log_stdout, "stdout")
    print_log_if_exists(process.log_stderr, "stderr")
