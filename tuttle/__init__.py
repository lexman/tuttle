#!/usr/bin/env python
# -*- coding: ascii -*-

__version__ ='0.1'

from project_parser import ProjectParser, ParsingError
from os import chdir, getcwd
from os.path import abspath

def prepare_workflow(tuttlefile, workspace):
    curdir = getcwd()
    abs_tuttlefile = abspath(tuttlefile)
    chdir(workspace)
    try:
        pp = ProjectParser()
        try:
            pp.parse_file(abs_tuttlefile)
        except ParsingError as e:
            print e
        missing = pp.missing_inputs()
        if missing:
            error_msg = "Missing the following resources to launch the workflow :\n"
            for mis in missing:
                error_msg += "* {}\n".format(mis.url)
            print error_msg
    except BaseException:
        chdir(curdir)
        raise
