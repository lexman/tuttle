# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE, check_output
from os.path import isfile, dirname, abspath, join

from os import path, environ, getcwd
from tests.functional_tests import isolate, run_tuttle_file
from shlex import split


class TestExtendWorkflow:

    def get_cmd_extend_workflow(self):
        """
        :return: A command line to call tuttle-extend-workflow even if tuttle has not been installed with pip
        """
        if environ.has_key('VIRTUAL_ENV'):
            py_cli = abspath(join(environ['VIRTUAL_ENV'], 'Scripts', 'python'))
        else:
            py_cli = 'python'
        extend = abspath(join(__file__, '..', '..', '..', 'bin', 'tuttle-extend-workflow'))
        cmd_extend = "{} {}".format(py_cli, extend)
        return cmd_extend

    def init_tuttle_project(self):
        # Creates .tuttle directory and subdirs for a tuttle project
        project = """file://B <- file://A
    echo A produces B > B"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

    @isolate(['A'])
    def test_create_extension(self):
        """ A preprocess should be able to call the tuttle-extend-workflow command"""
        self.init_tuttle_project()  # ensures there is a .tuttle directory
        extend = abspath(join(__file__, '..', '..', '..', 'bin', 'tuttle-extend-workflow'))
        output = check_output(['python', extend, 'b-produces-x', 'x="C"'])
        expected_file = join('.tuttle', 'extensions', 'extension_1')
        assert isfile(expected_file), output
