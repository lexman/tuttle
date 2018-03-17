#!/usr/bin/env python
# -*- coding: utf8 -*-

from argparse import ArgumentParser, ArgumentTypeError
from tuttle.version import version
from tuttle.extend_workflow import extend_workflow, ExtendError, extract_variables


def check_minus_1_or_positive(value):
    ivalue = int(value)
    if ivalue == 0 or ivalue < -1:
         raise ArgumentTypeError("%s is an invalid positive int value or -1" % value)
    return ivalue


def format_variable(name, value):
    if isinstance(value, list):
        res = "{}[]={}".format(name, " ".join(value))
    else:
        res = "{}={}".format(name, value)
    return res


def tuttle_extend_workflow_main():
    parser = ArgumentParser(
        description="Extends a workflow by adding a templated tuttle project. Must be run from a preprocessor in a "
                    "tuttle project - version {}".format(version)
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Display template and variables")
    parser.add_argument("template", help="template file")
    parser.add_argument('variables', help='variables to insert into the template int the form my_var="my value"',
                        nargs="*")
    parser.add_argument('-n', '--name',
                        default='extension',
                        dest='name',
                        help='Name of the extended workflow')
    params = parser.parse_args()

    try:
        vars_dic = extract_variables(params.variables)
        extend_workflow(params.template, name=params.name, **vars_dic)
        if params.verbose:
            print("Injecting into template {} :".format(params.template))
            for key, value in vars_dic.iteritems():
                print(" * {}".format(format_variable(key, value)))
    except ExtendError as e:
        print e.message
        exit(1)
