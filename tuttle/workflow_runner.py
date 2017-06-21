# -*- coding: utf8 -*-

"""
Utility methods for use in running workflows.
This module is responsible for the inner structure of the .tuttle directory
"""
from glob import glob
from shutil import rmtree
from os import remove, makedirs, getcwd
from os.path import join, isdir, isfile
from tuttle.error import TuttleError
from tuttle.utils import EnvVar
from tuttle.log_follower import LogsFollower

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
    def prepare_paths(process):
        log_stdout = join(WorkflowRuner._logs_dir, "{}_stdout.txt".format(process.id))
        log_stderr = join(WorkflowRuner._logs_dir, "{}_err.txt".format(process.id))
        reserved_path = join(WorkflowRuner._processes_dir, process.id)
        if isdir(reserved_path):
            rmtree(reserved_path)
        elif isfile(reserved_path):
            remove(reserved_path)
        return reserved_path, log_stdout, log_stderr

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
    def print_log_if_exists(log_file, header):
        if not isfile(log_file):
            return
        with open(log_file, "r") as f:
            content = f.read()
            if len(content) > 1:
                print "--- {} : {}".format(header, "-" * (60 - len(header) - 7))
                print content

    @staticmethod
    def print_logs(process):
        WorkflowRuner.print_log_if_exists(process.log_stdout, "stdout")
        WorkflowRuner.print_log_if_exists(process.log_stderr, "stderr")

    @staticmethod
    def list_extensions():
        path = join(WorkflowRuner._extensions_dir, '*')
        return glob(path)

    @staticmethod
    def get_logger():
        return LogsFollower.get_logger()

    @staticmethod
    def resources2list(urls):
        res = "\n".join(("* {}".format(url) for url in urls))
        return res

    @staticmethod
    def run_workflow(workflow):
        """ Runs a workflow by running every process in the right order

        :return:
        :raises ExecutionError if an error occurs
        """
        # TODO create tuttle dirs only once
        WorkflowRuner.create_tuttle_dirs()
        lt = LogsFollower()
        logger = LogsFollower.get_logger()
        with lt.trace_in_background():
            nb_process_run = 0
            process = workflow.pick_a_process_to_run()
            while process is not None:
                nb_process_run += 1
                WorkflowRuner.print_header(process, logger)
                try:
                    reserved_path, log_stdout, log_stderr = WorkflowRuner.prepare_paths(process)
                    lt.follow_process(logger, log_stdout, log_stderr)
                    process.run(reserved_path, log_stdout, log_stderr)
                    missing_outputs = process.missing_outputs()
                    if missing_outputs:
                        process.post_fail()
                        msg = "After execution of process {} : these resources " \
                              "should have been created : \n{} ".format(process.id, WorkflowRuner.resources2list(
                            missing_outputs))
                        raise ResourceError(msg)
                    workflow.update_signatures(process)
                finally:
                    workflow.dump()
                    workflow.create_reports()
                process = workflow.pick_a_process_to_run()
        return nb_process_run


class TuttleEnv(EnvVar):
    """
    Adds the 'TUTTLE_ENV' environment variable so subprocesses can find the .tuttle directory.
    """
    def __init__(self):
        directory = join(getcwd(), '.tuttle')
        super(TuttleEnv, self).__init__('TUTTLE_ENV', directory)
