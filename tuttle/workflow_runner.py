# -*- coding: utf8 -*-

"""
Utility methods for use in running workflows.
This module is responsible for the inner structure of the .tuttle directory
"""
from multiprocessing import Pool, cpu_count
import multiprocessing
from os.path import abspath
from traceback import format_exception

from tuttle.error import TuttleError
from tuttle.utils import EnvVar
from tuttle.log_follower import LogsFollower
from time import sleep
import sys
import logging
import psutil


LOGGER = logging.getLogger(__name__)


def print_process_header(process, logger):
    pid = multiprocessing.current_process().pid
    msg = "{}\nRunning process {} (pid={})".format("=" * 60, process.id, pid)
    logger.info(msg)


def resources2list(resources):
    res = "\n".join(("* {}".format(resource.url) for resource in resources))
    return res


def output_signatures(process):
    result = {resource.url : str(resource.signature()) for resource in process.iter_outputs()}
    return result


# This is a free method, because it will be serialized and passed
# to another process, so it must not be linked to objects nor
# capture closures
def run_process_without_exception(process):
    multiprocessing.current_process().name = process.id
    try:
        print_process_header(process, LOGGER)
        process._processor.run(process, process._reserved_path, process.log_stdout, process.log_stderr)
    except TuttleError as e:
        return False, str(e), None
    except Exception:
        exc_info = sys.exc_info()
        stacktrace = "".join(format_exception(*exc_info))
        error_msg = "An unexpected error have happen in tuttle processor {} : \n" \
                    "{}\n" \
                    "Process {} will not complete.".format(process._processor.name, stacktrace, process.id)
        return False, error_msg, None
    try:
        missing_outputs = process.missing_outputs()
    except Exception:
        exc_info = sys.exc_info()
        stacktrace = "".join(format_exception(*exc_info))
        error_msg = "An unexpected error have happen in tuttle while checking existence of output resources " \
                    "after process {} has run: \n" \
                    "{}\n" \
                    "Process cannot be considered complete.".format(process.id, stacktrace)
        return False, error_msg, None
    if missing_outputs:
        msg = "After execution of process {} : these resources " \
              "should have been created : \n{} ".format(process.id, resources2list(missing_outputs))
        return False, msg, None
    try:
        signatures = output_signatures(process)
    except Exception:
        exc_info = sys.exc_info()
        stacktrace = "".join(format_exception(*exc_info))
        error_msg = "An unexpected error have happen in tuttle while retrieving signature after process {} has run: " \
                    "\n{}\n" \
                    "Process cannot be considered complete.".format(process.id, stacktrace)
        return False, error_msg, None
    return True, None, signatures


class WorkflowRuner:

    @staticmethod
    def resources2list(resources):
        res = "\n".join(("* {}".format(resource.url) for resource in resources))
        return res

    def __init__(self, nb_workers):
        self._lt = LogsFollower()
        self._logger = WorkflowRuner.get_logger()
        self._pool = None
        if nb_workers == -1:
            self._nb_workers = int((cpu_count() + 1) / 2)
        else:
            self._nb_workers = nb_workers
        self._free_workers = None
        self._completed_processes = []

    def start_process_in_background(self, process):
        self.acquire_worker()

        def process_run_callback(result):
            success, error_msg, signatures = result
            process.set_end(success, error_msg)
            self.release_worker()
            self._completed_processes.append((process, signatures))

        process.set_start()
        resp = self._pool.apply_async(run_process_without_exception, [process], callback = process_run_callback)

    def start_processes_on_available_workers(self, runnables):
        started_a_process = False
        while self.workers_available() and runnables:
            # No error
            process = runnables.pop()
            self.start_process_in_background(process)
            started_a_process = True
        return started_a_process

    def handle_completed_process(self, workflow, runnables, success_processes, failure_processes):
        handled_completed_process = False
        while self._completed_processes:
            completed_process, signatures = self._completed_processes.pop()
            if completed_process.success:
                success_processes.append(completed_process)
                workflow.update_signatures(signatures)
                new_runnables = workflow.discover_runnable_processes(completed_process)
                runnables.update(new_runnables)
            else:
                failure_processes.append(completed_process)
            handled_completed_process = True
        return handled_completed_process

    def run_parallel_workflow(self, workflow, keep_going=False):
        """ Runs a workflow by running every process in the right order
        :return: success_processes, failure_processes :
        list of processes ended with success, list of processes ended with failure
        """
        for process in workflow.iter_processes():
            if process.start is None:
                # Don't display logs if the process has already run
                self._lt.follow_process(process.log_stdout, process.log_stderr, process.id)

        failure_processes, success_processes = [], []
        with self._lt.trace_in_background():
            self.init_workers()
            runnables = workflow.runnable_processes()
            while (keep_going or not failure_processes) and (self.active_workers() or self._completed_processes or runnables):
                started_a_process = self.start_processes_on_available_workers(runnables)
                handled_completed_process = self.handle_completed_process(workflow, runnables, success_processes, failure_processes)
                if handled_completed_process or started_a_process:
                    workflow.dump()
                    workflow.create_reports()
                else:
                    sleep(0.1)
            if failure_processes and not keep_going:
                self._logger.error("Process {} has failled".format(failure_processes[0].id))
                self._logger.warn("Waiting for all processes already started to complete")
                # self._logger.warn("Press ^C to stop everything.")
                while self.active_workers() or self._completed_processes:
                    handled_completed_process = self.handle_completed_process(workflow, runnables, success_processes, failure_processes)
                    if handled_completed_process:
                        workflow.dump()
                        workflow.create_reports()
                    else:
                        sleep(0.1)

            self.terminate_workers_and_clean_subprocesses()
#        if failure_processes:
#            WorkflowRuner.mark_unfinished_processes_as_failure(workflow)

        return success_processes, failure_processes

    def init_workers(self):
        self._pool = Pool(self._nb_workers)
        self._free_workers = self._nb_workers

    def terminate_workers_and_clean_subprocesses(self):
        direct_procs = set(psutil.Process().children())
        all_procs = set(psutil.Process().children(recursive=True))
        sub_procs = all_procs - direct_procs

        # Terminate cleanly direct procs instanciated by multiprocess
        self._pool.terminate()
        self._pool.join()

        # Then terminate subprocesses that have not been terminated
        for p in sub_procs:
            p.terminate()
        gone, still_alive = psutil.wait_procs(sub_procs, timeout=2)
        for p in still_alive:
            p.kill()


    def acquire_worker(self):
        assert self._free_workers > 0
        self._free_workers -= 1

    def release_worker(self):
        self._free_workers += 1

    def workers_available(self):
        return self._free_workers

    def active_workers(self):
        return self._free_workers != self._nb_workers

    @staticmethod
    def mark_unfinished_processes_as_failure(workflow):
        for process in workflow.iter_processes():
            if process.start and not process.end:
                error_msg = "This process was canceled because another process has failed"
                process.set_end(False, error_msg)
        workflow.dump()
        workflow.create_reports()

    @staticmethod
    def print_preprocess_header(process, logger):
        logger.info("-" * 60)
        logger.info("Preprocess : {}".format(process.id))
        logger.info("-" * 60)

    @staticmethod
    def print_preprocesses_header():
        print("=" * 60)
        print("Running preprocesses for this workflow")
        print("=" * 60)

    @staticmethod
    def print_preprocesses_footer():
        print("=" * 60)
        print("End of preprocesses... Running the workflow")
        print("=" * 60)

    @staticmethod
    def get_logger():
        logger = logging.getLogger(__name__)
        formater = logging.Formatter("%(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formater)
        handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        return logger


class TuttleEnv(EnvVar):
    """
    Adds the 'TUTTLE_ENV' environment variable so subprocesses can find the .tuttle directory.
    """
    def __init__(self):
        directory = abspath('.tuttle')
        super(TuttleEnv, self).__init__('TUTTLE_ENV', directory)
