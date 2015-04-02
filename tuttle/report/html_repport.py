#!/usr/bin/env python
# -*- coding: utf8 -*-

from jinja2 import Template
from os import path, mkdir
from shutil import copytree
from time import strftime, localtime
from dot_repport import dot


def format_process(process):
    duration = ""
    start = ""
    end = ""
    return_code = ""
    if process.start:
        start = strftime("%a, %d %b %Y %H:%M:%S", localtime(process.start))
        if process.end:
            end = strftime("%a, %d %b %Y %H:%M:%S", localtime(process.end))
            duration = process.end - process.start
            return_code = process.return_code

    return {
        'id' : process.id,
        'start' : start,
        'end' : end,
        'duration' : duration,
        'log_stdout' : process.log_stdout,
        'log_stderr' : process.log_stderr,
        'outputs' : process.outputs,
        'inputs' : process.inputs,
        '_code' : process._code,
        'return_code' : return_code,
    }

def ensure_assets(module_dir, file_dir):
    tuttle_dir = path.join(file_dir, '.tuttle')
    if not path.isdir(tuttle_dir):
        mkdir(tuttle_dir)
    assets_dir = path.join(file_dir, '.tuttle', 'html_report_assets')
    if not path.isdir(assets_dir):
        copytree(path.join(module_dir, 'html_report_assets', ''), assets_dir,)

def create_html_report(workflow, filename):
    """ Write an html file describing the workflow
    :param workflow:
    :param filename: path to the html fil to be generated
    :return: None
    """
    module_dir = path.dirname(__file__)
    file_dir = path.dirname(filename)
    ensure_assets(module_dir, file_dir)
    tpl_filename = path.join(module_dir, "report_template.html")
    with open(tpl_filename, "r") as ftpl:
        t = Template(ftpl.read())
    processes = [format_process(p) for p in workflow.processes]
    with open(filename, "w") as fout:
        fout.write(t.render(processes = processes, dot_src = dot(workflow)))
