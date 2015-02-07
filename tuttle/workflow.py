#!/usr/bin/env python
# -*- coding: utf8 -*-


class Workflow:
    """ A workflow is a dependency tree of processes
    """
    def __init__(self):
        self.processes = []

    def add_process(self, process):
        """ Adds a process
        :param process:
        :return:
        """
        self.processes.append(process)

    def pick_a_process_to_run(self):
        """ Pick up a process to run
        :return:
        """
        #TODO : check for circular references
        for process in self.processes:
            # All outputs are supposed to be generated at the same time with a process,
            # so checking for existence of one is like checking fo existence of all !
            if len(process._outputs) > 0 and not process._outputs[0].exists():
                for in_res in process._inputs:
                    if not in_res.exists():
                        # Can't pick this one if all dependencies have not been generated !
                        continue
                # Every input is here, so the process can be run !
                return process
        return None