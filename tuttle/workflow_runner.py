# -*- coding: utf8 -*-

"""
Utility methods for use in running workflows.
This module is responsible for the inner structure of the .tuttle directory
"""
from glob import glob
from multiprocessing import Pool
from shutil import rmtree
from os import remove, makedirs, getcwd
from os.path import join, isdir, isfile
from tuttle.error import TuttleError
from tuttle.utils import EnvVar
from tuttle.log_follower import LogsFollower
from time import sleep
import sys


# This is a free method, because it will be serialized and passed
# to another process, so it must not be linked to objects nor
# capture closures
def run_process_without_exception(process):
    try:
        process._processor.run(process, process._reserved_path, process.log_stdout, process.log_stderr)
        WorkflowRuner.raise_if_missing_process_outputs(process)
    except Exception as e:
        process.set_end(False)
        return False, e
    process.set_end(True)
    return True, None


class ResourceError(TuttleError):
    pass


def tuttle_dir(*args):
    return join('.tuttle', *args)


class WorkflowRuner():

    _processes_dir = tuttle_dir('processes')
    _logs_dir = tuttle_dir('processes', 'logs')
    _extensions_dir = tuttle_dir('extensions')

    @staticmethod
    def tuttle_dir(*args):
        return join('.tuttle', *args)

    @staticmethod
    def resources2list(resources):
        res = "\n".join(("* {}".format(resource.url) for resource in resources))
        return res

    @staticmethod
    def raise_if_missing_process_outputs(process):
        missing_outputs = process.missing_outputs()
        if missing_outputs:
            msg = "After execution of process {} : these resources " \
                  "should have been created : \n{} ".format(process.id, WorkflowRuner.resources2list(
                missing_outputs))
            raise ResourceError(msg)

    def __init__(self, poolsize):
        self._lt = LogsFollower()
        self._logger = LogsFollower.get_logger()
        self._pool = None
        self._poolsize = poolsize
        self._free_workers = None
        self._completed_processes = set()
        self._errors = []

    def acquire_worker(self):
        self._free_workers -= 1

    def release_worker(self):
        self._free_workers += 1

    def workers_available(self):
        return self._free_workers

    def active_workers(self):
        return self._free_workers != self._poolsize

    def start_process_in_background(self, process, workflow):
        self.acquire_worker()

        def process_run_callback(result):
            success, e = result
            process.set_end(success)
            self.release_worker()
            self._completed_processes.add(process)
            if not success:
                self._errors.append(e)

        process.set_start()
        WorkflowRuner.print_header(process, self._logger)
        resp = self._pool.apply_async(run_process_without_exception, [process], callback = process_run_callback)

    def run_parallel_processes(self, workflow):
        nb_process_run = 0
        runnables = workflow.runnable_processes()
        error = False
        while not error and (self.active_workers() or self._completed_processes or runnables):
            started_a_process = False
            while self.workers_available() and runnables:
                # No error
                process = runnables.pop()
                self.start_process_in_background(process, workflow)
                started_a_process = True

            handled_completed_process = False
            while self._completed_processes:
                completed_process = self._completed_processes.pop()
                if completed_process.success:
                    workflow.update_signatures(completed_process)
                else:
                    error = True
                new_runnables = workflow.discover_runnable_processes(completed_process)
                runnables.update(new_runnables)
                handled_completed_process = True
                nb_process_run += 1
            if handled_completed_process:
                workflow.dump()
                workflow.create_reports()

            if not (handled_completed_process or started_a_process):
                sleep(0.1)
        if self._errors:
            # TODO this fucks up the stacktrace
            raise self._errors[0]
        return nb_process_run

    def run_parallel_workflow(self, workflow):
        """ Runs a workflow by running every process in the right order

        :return:
        :raises ExecutionError if an error occurs
        """
        # TODO create tuttle dirs only once
        WorkflowRuner.create_tuttle_dirs()
        for process in workflow.iter_processes():
            WorkflowRuner.prepare_and_assign_paths(process)
            self._lt.follow_process(self._logger, process.log_stdout, process.log_stderr)

        with self._lt.trace_in_background():
            self._pool = Pool(self._poolsize)
            self._free_workers = self._poolsize
            try:
                nb_process_run = self.run_parallel_processes(workflow)
            finally:
                self._pool.terminate()
                self._pool.join()
                WorkflowRuner.mark_unfinished_processes_as_failure(workflow)
        return nb_process_run

    @staticmethod
    def mark_unfinished_processes_as_failure(workflow):
        for process in workflow.iter_processes():
            if process.start and not process.end:
                process.set_end(False)
        workflow.dump()
        workflow.create_reports()

    @staticmethod
    def prepare_and_assign_paths(process):
        log_stdout = join(WorkflowRuner._logs_dir, "{}_stdout.txt".format(process.id))
        log_stderr = join(WorkflowRuner._logs_dir, "{}_err.txt".format(process.id))
        # It would be a good idea to clean up all directories before
        # running the whole workflow
        # For the moment we clean here : before folowing the logs
        if isfile(log_stdout):
            remove(log_stdout)
        if isfile(log_stderr):
            remove(log_stderr)
        reserved_path = join(WorkflowRuner._processes_dir, process.id)
        if isdir(reserved_path):
            rmtree(reserved_path)
        elif isfile(reserved_path):
            remove(reserved_path)
        process.assign_paths(reserved_path, log_stdout, log_stderr)

    @staticmethod
    def create_tuttle_dirs():
        if not isdir(WorkflowRuner._processes_dir):
            makedirs(WorkflowRuner._processes_dir)
        if not isdir(WorkflowRuner._logs_dir):
            makedirs(WorkflowRuner._logs_dir)

    @staticmethod
    def empty_extension_dir():
        if not isdir(WorkflowRuner._extensions_dir):
            makedirs(WorkflowRuner._extensions_dir)
        else:
            rmtree(WorkflowRuner._extensions_dir)
            makedirs(WorkflowRuner._extensions_dir)

    @staticmethod
    def print_header(process, logger):
        logger.info("=" * 60)
        logger.info(process.id)
        logger.info("=" * 60)

    @staticmethod
    def print_preprocess_header(process, logger):
        logger.info("-" * 60)
        logger.info("Preprocess : {}".format(process.id))
        logger.info("-" * 60)

    @staticmethod
    def print_preprocesses_header():
        print "=" * 60
        print "Running preprocesses for this workflow"
        print "=" * 60

    @staticmethod
    def print_preprocesses_footer():
        print "=" * 60
        print "End of preprocesses... Running the workflow"
        print "=" * 60

    @staticmethod
    def print_log_if_exists_old(log_file, header):
        if not isfile(log_file):
            return
        with open(log_file, "r") as f:
            content = f.read()
            if len(content) > 1:
                print "--- {} : {}".format(header, "-" * (60 - len(header) - 7))
                print content

    @staticmethod
    def print_logs_old(process):
        WorkflowRuner.print_log_if_exists(process.log_stdout, "stdout")
        WorkflowRuner.print_log_if_exists(process.log_stderr, "stderr")

    @staticmethod
    def list_extensions():
        path = join(WorkflowRuner._extensions_dir, '*')
        return glob(path)

    @staticmethod
    def get_logger():
        return LogsFollower.get_logger()


class TuttleEnv(EnvVar):
    """
    Adds the 'TUTTLE_ENV' environment variable so subprocesses can find the .tuttle directory.
    """
    def __init__(self):
        directory = join(getcwd(), '.tuttle')
        super(TuttleEnv, self).__init__('TUTTLE_ENV', directory)
