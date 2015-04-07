# -*- coding: utf8 -*-
from tuttle import workflow

__version__ = '0.1'

from error import TuttleError
from project_parser import ProjectParser
from workflow import Workflow
from invalidation import invalidate


def parse_invalidate_and_run(tuttlefile):
        try:
            pp = ProjectParser()
            workflow = pp.parse_and_check_file(tuttlefile)
            workflow.pre_check_processes()
            invalidate(workflow)
            workflow.create_reports()
            workflow.run()
        except TuttleError as e:
            print e
            return 2
        return 0
