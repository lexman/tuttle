# -*- coding: utf8 -*-

"""
Utility methods for use in running workflows.
This module is responsible for the inner structure of the .tuttle directory
"""

from shutil import rmtree
from os import remove, makedirs, getcwd
from os.path import join, isdir, isfile
from tuttle.error import TuttleError
from tuttle.utils import EnvVar


class ResourceError(TuttleError):
    pass


def tuttle_dir(*args):
    return join('.tuttle', *args)


_processes_dir = tuttle_dir('processes')
_logs_dir = tuttle_dir('processes', 'logs')
_extensions_dir = tuttle_dir('extensions')


def prepare_paths(process):
    log_stdout = join(_logs_dir, "{}_stdout.txt".format(process.id))
    log_stderr = join(_logs_dir, "{}_err.txt".format(process.id))
    reserved_path = join(_processes_dir, process.id)
    if isdir(reserved_path):
        rmtree(reserved_path)
    elif isfile(reserved_path):
        remove(reserved_path)
    return reserved_path, log_stdout, log_stderr


def create_tuttle_dirs():
    if not isdir(_processes_dir):
        makedirs(_processes_dir)
    if not isdir(_logs_dir):
        makedirs(_logs_dir)


def empty_extension_dir():
    if not isdir(_extensions_dir):
        makedirs(_extensions_dir)
    else:
        rmtree(_extensions_dir)
        makedirs(_extensions_dir)


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


class TuttleEnv(EnvVar):
    """
    Adds the 'TUTTLE_ENV' environment variable so subprocesses can find the .tuttle directory.
    """
    def __init__(self):
        directory = join(getcwd(), '.tuttle')
        super(TuttleEnv, self).__init__('TUTTLE_ENV', directory)
