# -*- coding: utf8 -*-
from glob import glob
from itertools import chain
from os.path import join, isfile, isdir, basename, exists
from os import remove, makedirs
from shutil import rmtree, move


def tuttle_dir(*args):
    return join('.tuttle', *args)


class TuttleDirectories:

    _processes_dir = tuttle_dir('processes')
    _logs_dir = tuttle_dir('processes', 'logs')
    _extensions_dir = tuttle_dir('extensions')

    @staticmethod
    def tuttle_dir(*args):
        return tuttle_dir(*args)
        #return join('.tuttle', *args)

    @staticmethod
    def list_extensions():
        path = join(TuttleDirectories._extensions_dir, '*')
        return glob(path)

    @staticmethod
    def prepare_and_assign_paths(process):
        log_stdout = join(TuttleDirectories._logs_dir, "{}_stdout.txt".format(process.id))
        log_stderr = join(TuttleDirectories._logs_dir, "{}_err.txt".format(process.id))
        # It would be a good idea to clean up all directories before
        # running the whole workflow
        # For the moment we clean here : before folowing the logs
        if isfile(log_stdout):
            remove(log_stdout)
        if isfile(log_stderr):
            remove(log_stderr)
        reserved_path = join(TuttleDirectories._processes_dir, process.id)
        if isdir(reserved_path):
            rmtree(reserved_path)
        elif isfile(reserved_path):
            remove(reserved_path)
        process.assign_paths(reserved_path, log_stdout, log_stderr)

    @staticmethod
    def create_tuttle_dirs():
        if not isdir(TuttleDirectories._processes_dir):
            makedirs(TuttleDirectories._processes_dir)
        if not isdir(TuttleDirectories._logs_dir):
            makedirs(TuttleDirectories._logs_dir)

    @staticmethod
    def empty_extension_dir():
        if not isdir(TuttleDirectories._extensions_dir):
            makedirs(TuttleDirectories._extensions_dir)
        else:
            rmtree(TuttleDirectories._extensions_dir)
            makedirs(TuttleDirectories._extensions_dir)

    @staticmethod
    def move_paths_from(process, from_path):
        reserved_path = join(from_path, basename(process._reserved_path))
        log_stdout = join(from_path, 'logs', basename(process.log_stdout))
        log_stderr = join(from_path, 'logs', basename(process.log_stderr))
        TuttleDirectories.prepare_and_assign_paths(process)
        # Some process don't create all the necessary files
        if exists(reserved_path):
            move(reserved_path, process._reserved_path)
        #if exists(log_stdout):
        move(log_stdout, process.log_stdout)
        #if exists(log_stdout):
        move(log_stderr, process.log_stderr)

    @staticmethod
    def straighten_out_process_and_logs(workflow):
        tmp_processes = TuttleDirectories.tuttle_dir('tmp_processes')
        rmtree(tmp_processes, True)
        move(TuttleDirectories._processes_dir, tmp_processes)
        TuttleDirectories.create_tuttle_dirs()
        for process in chain(workflow.iter_processes(), workflow.iter_preprocesses()):
            if process.start is not None:
                TuttleDirectories.move_paths_from(process, tmp_processes)
            else:
                TuttleDirectories.prepare_and_assign_paths(process)
        rmtree(tmp_processes)
