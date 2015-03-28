#!/usr/bin/env python
# -*- coding: utf8 -*-
from tuttle.process import ProcessState

DOT_HEADER = """digraph workflow {
    Node [style="rounded,filled", shape=box, fillcolor=none]
"""


def color_from_process(process):
    color = "none"
    if process.start:
        if not process.end:
            # Running
            color = "skyblue"
        elif not process.return_code:
            # success
            color = "green"
        else:
            color = "red"

    return color

def create_dot_report(workflow, filename):
    """ Write to disk a dot file describing the workflow, with color for states

    :return: None
    """
    with open(filename, "w") as fout:
        # TODO
        # Add a legend
        # Show primary resources in a color, and missing ones in another
        fout.write(DOT_HEADER)
        for process in workflow.processes:
            p_node = "p_{}".format(process.id())
            fout.write('    {} [shape="none", label="", width=0, height=0] ;\n'.format(p_node))
            for res_input in process._inputs:
                fout.write('    "{}" -> {} [arrowhead="none"] \n'.format(workflow.nick_from_url(res_input.url), p_node))
            color = color_from_process(process)
            for res_output in process._outputs:
                nick = workflow.nick_from_url(res_output.url)
                fout.write('    {} -> "{}" \n'.format(p_node, nick))
                fout.write('    "{}" [fillcolor={}] ;\n'.format(nick, color))
        fout.write('}')
