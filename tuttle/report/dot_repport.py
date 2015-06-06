# -*- coding: utf8 -*-

DOT_HEADER = """digraph workflow {
    Node [style="rounded,filled", shape=box, fillcolor=none]
"""


def color_from_process(process):
    color = "none"
    if process.start:
        if not process.end:
            # Running
            color = "skyblue"
        elif process.success:
            # success
            color = "green"
        else:
            color = "red"
    return color


# TODO nick names for resources should be uniq
def nick_from_url(url):
    parts = url.split("/")
    return parts.pop()


def dot(workflow):
    # TODO :
    # * Add a legend
    # * Show missing resources in a different another
    result = DOT_HEADER
    for process in workflow.iter_processes():
        color = color_from_process(process)
        p_node = "p_{}".format(process.id)
        if color != "none":
            fontcolor = color
        else:
            fontcolor = "black"
        result += '    {} [label="{}", URL="#{}", color={}, fontcolor={}, width=0, height=0] ' \
                  ';\n'.format(p_node, process.id, process.id, color, fontcolor)
        for res_input in process.iter_inputs():
            nick = nick_from_url(res_input.url)
            result += '    "{}" -> {} [arrowhead="none"] \n'.format(nick, p_node)
            if res_input.is_primary():
                result += '    "{}" [fillcolor=beige] ;\n'.format(nick)
        for res_output in process.iter_outputs():
            nick = nick_from_url(res_output.url)
            result += '    {} -> "{}" \n'.format(p_node, nick)
            result += '    "{}" [fillcolor={}] ;\n'.format(nick, color)
    result += '}'
    return result
