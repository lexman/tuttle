#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
from os.path import abspath, exists
from argparse import ArgumentParser, ArgumentTypeError
from tuttle.commands import parse_invalidate_and_run, invalidate_resources
from tuttle.utils import CurrentDir
from tuttle.version import version
from tuttle.extend_workflow import extend_workflow, ExtendError, extract_variables


def check_minus_1_or_positive(value):
    ivalue = int(value)
    if ivalue == 0 or ivalue < -1:
         raise ArgumentTypeError("%s is an invalid positive int value or -1" % value)
    return ivalue


def tuttle_main():
    try:
        parser = ArgumentParser(
            description="Runs a workflow - version {}".format(version)
        )
        parent_parser = ArgumentParser(
            add_help=False
        )
        parent_parser.add_argument('-f', '--file',
                          default='tuttlefile',
                          dest='tuttlefile',
                          help='Path to the tuttlefile : project file describing the workflow')
        parent_parser.add_argument('-w', '--workspace',
                          default='.',
                          dest='workspace',
                          help='Directory where the workspace lies. Default is the current directory')
        parent_parser.add_argument('-t', '--threshold',
                          default='-1',
                          type=int,
                          dest='threshold',
                          help='Threshold for invalidation : \n'
                               '0 - prevents any invalidation \n'
                               'N - prevents invalidation if lost processing time >= N\n'
                               '-1 (default) - no verification')
        subparsers = parser.add_subparsers(help='commands help', dest='command')
        parser_run = subparsers.add_parser('run', parents=[parent_parser],
                                           help='Run the missing part of workflow')
        parser_run.add_argument('-j', '--jobs',
                                help='Number of workers (to run processes in parallel)\n'
                                     '-1 = half of the number of cpus',
                                default=1,
                                type=check_minus_1_or_positive)
        parser_run.add_argument('-k', '--keep-going',
                                help="Don't stop when a process fail : run all the processes you can",
                                default=False,
                                dest='keep_going',
                                action="store_true")
        parser_run.add_argument('-i', '--check-integrity',
                                help="Check integrity of all resources in case some have changed outside of tuttle.\n"
                                     "Requires to compute signature of every resource produced by tuttle, which can "
                                     "can be time consuming eg for big files or database tables.",
                                default=False,
                                dest='check_integrity',
                                action="store_true")
        parser_invalidate = subparsers.add_parser('invalidate', parents=[parent_parser],
                                                  help='Remove some resources already computed and all their dependencies')
        parser_invalidate.add_argument('resources', help='url of the resources to invalidate', nargs="*")
        params = parser.parse_args(sys.argv[1:])

        tuttlefile_path = abspath(params.tuttlefile)
        if not exists(tuttlefile_path):
            print "No tuttlefile"
            sys.exit(2)
        with CurrentDir(params.workspace):
            if params.command == 'run':
                return parse_invalidate_and_run(tuttlefile_path, params.threshold, params.jobs, params.keep_going, params.check_integrity)
            elif params.command == 'invalidate':
                return invalidate_resources(tuttlefile_path, params.resources, params.threshold)
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(2)


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
