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


def dot(workflow):
    # TODO
    # Add a legend
    # Show primary resources in a color, and missing ones in another
    result = DOT_HEADER
    for process in workflow.processes:
        p_node = "p_{}".format(process.id)
        result += '    {} [shape="none", label="{}", URL="#{}", width=0, height=0] ;\n'.format(p_node, process.id, process.id)
        for res_input in process.inputs:
            nick = workflow.nick_from_url(res_input.url)
            result += '    "{}" -> {} [arrowhead="none"] \n'.format(nick, p_node)
            if res_input.creator_process is None:
                result += '    "{}" [fillcolor=beige] ;\n'.format(nick)
        color = color_from_process(process)
        for res_output in process.outputs:
            nick = workflow.nick_from_url(res_output.url)
            result += '    {} -> "{}" \n'.format(p_node, nick)
            result += '    "{}" [fillcolor={}] ;\n'.format(nick, color)
    result += '}'
    return result
