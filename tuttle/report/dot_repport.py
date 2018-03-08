# -*- coding: utf8 -*-

from os import path


DOT_HEADER = """digraph workflow {
    rankdir="LR";
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


def dot_id(url):
    import urllib
    return urllib.quote(url)


def process_node_id(id):
    p_node = '"p_{}"'.format(id)
    return p_node


def dot(workflow):
    # TODO :
    # * Add a legend
    # * Show missing resources in a different color
    result = DOT_HEADER
    for process in workflow.iter_processes():
        color = color_from_process(process)
        p_node = process_node_id(process.id)
        if color != "none":
            fontcolor = color
        else:
            fontcolor = "black"
        result += '    {} [label="{}", URL="#{}", color={}, fontcolor={}, width=0, height=0] ' \
                  ';\n'.format(p_node, process.id, process.id, color, fontcolor)
        for res_input in process.iter_inputs():
            nick = nick_from_url(res_input.url)
            resource_id = dot_id(res_input.url)
            result += '    "{}" -> {} [arrowhead="none"] \n'.format(resource_id,  p_node)
            if res_input.is_primary():
                result += '    "{}" [fillcolor=beige, label="{}"] ;\n'.format(resource_id, nick)
        for res_output in process.iter_outputs():
            nick = nick_from_url(res_output.url)
            resource_id = dot_id(res_output.url)
            result += '    {} -> "{}" \n'.format(p_node, resource_id)
            result += '    "{}" [fillcolor={}, label="{}"] ;\n'.format(resource_id, color, nick)
    result += '}'
    return result


def create_dot_report(workflow, filename):
    """ Write an html file describing the workflow
    :param workflow:
    :param filename: path to the html fil to be generated
    :return: None
    """
    with open(filename, 'wb') as fout:
        dot_src = dot(workflow)
        fout.write(dot_src.encode('utf8)'))
