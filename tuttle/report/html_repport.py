#!/usr/bin/env python
# -*- coding: utf8 -*-

from jinja2 import Template
from os import path


def create_html_report(workflow, filename):
    """ Write an html file describing the workflow
    :param workflow:
    :param filename: path to the html fil to be generated
    :return: None
    """
    module_dir = path.dirname(__file__)
    tpl_filename = path.join(module_dir, "report_template.html")
    with open(tpl_filename, "r") as ftpl:
        t = Template(ftpl.read())
    with open(filename, "w") as fout:
        fout.write(t.render(processes = workflow.processes))
