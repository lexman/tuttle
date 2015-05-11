# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
from os.path import abspath, join, dirname
from tests.functional_tests import isolate, run_tuttle_file


class TestCommands():

    @isolate(['A'])
    def test_command_invalidate(self):
        """ Should display a message if there is no tuttlefile in the current directory"""
        project = """file://B <- file://A
            echo A creates B
            echo A creates B > B
            """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0

        dir = dirname(__file__)
        tuttle_cmd = abspath(join(dir, '..', '..', 'bin', 'tuttle'))
        proc = Popen(['python', tuttle_cmd, 'invalidate', 'file://B'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 0, output
        assert output.find('validate') >= 0, output
        assert output.find('* file://B') >= 0, output

    @isolate
    def test_invalidate_no_tuttle_file(self):
        """ Should display a message when launching invalidate and there is tuttlefile in the current directory"""
        dir = dirname(__file__)
        tuttle_cmd = abspath(join(dir, '..', '..', 'bin', 'tuttle'))
        proc = Popen(['python', tuttle_cmd, 'invalidate', 'file://B'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2, output
        assert output.find('No tuttlefile') >= 0, output

    @isolate
    def test_invalidate_nothing_have_run(self):
        """ Should display a message when launching invalidate and tuttle hasn't been run before : noting to invaidate"""
        project = """file://B <- file://A
            echo A creates B
            echo A creates B > B
            """
        open('tuttlefile', 'wb').write(project)
        dir = dirname(__file__)
        tuttle_cmd = abspath(join(dir, '..', '..', 'bin', 'tuttle'))
        proc = Popen(['python', tuttle_cmd, 'invalidate'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2, output
        assert output.find("Tuttle has not run yet ! It has produced nothing, so there is nothing to invalidate.") >= 0, output

    @isolate(['A'])
    def test_try_invalidate_bad_project(self):
        """ Should display a message if the tuttlefile is incorrect"""
        project = """file://B <- file://A
            echo A creates B
            echo A creates B > B
            """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0

        bad_project = """file://B <- file://A,
            echo A creates B
            echo A creates B > B
            """
        open('tuttlefile', 'wb').write(bad_project)

        dir = dirname(__file__)
        tuttle_cmd = abspath(join(dir, '..', '..', 'bin', 'tuttle'))
        proc = Popen(['python', tuttle_cmd, 'invalidate', 'file://B'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2, output
        assert output.find('Invalidation has failed because tuttlefile is has errors') >= 0, output
