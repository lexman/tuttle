#!/usr/bin/env python
# -*- coding: utf8 -*-


class Workflow:
    """ A workflow is a dependency tree of processes
    """
    def __init__(self):
        self.resources = {}
        self.processes = []

    def add_process(self, process):
        self.processes.append(process)

