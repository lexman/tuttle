#!/usr/bin/env python
# -*- coding: ascii -*-

__version__ ='0.1'

from project_parser import ProjectParser, ParsingError
from os import chdir, getcwd
from os.path import abspath
from time import time

def prepare_workflow(tuttlefile, workspace):
    curdir = getcwd()
    abs_tuttlefile = abspath(tuttlefile)
    chdir(workspace)
    try:
        pp = ProjectParser()
        try:
            workflow = pp.parse_file(abs_tuttlefile)
        except ParsingError as e:
            print e
            return
        missing = pp.missing_inputs()
        if missing:
            error_msg = "Missing the following resources to launch the workflow :\n"
            for mis in missing:
                error_msg += "* {}\n".format(mis.url)
            print error_msg
        else:
            return workflow
    finally:
        chdir(curdir)

def run_workflow(workflow):
    """ Runs all the needed processes in a workflow
    :param workflow: Workflow
    :return:
    """
    process = workflow.pick_a_process_to_run()
    while process is not None:
        process.generate_executable()
        process.start = time()
        process.return_code = process.run()
        process.end = time()
        process = workflow.pick_a_process_to_run()


