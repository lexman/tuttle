# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
from os.path import abspath, join, dirname

from tests.functional_tests import isolate


class TestNoTuttlefile():

    @isolate
    def test_no_file_in_current_dir(self):
        """ Should display a message if there is no tuttlefile in the current directory"""
        proc = Popen(['tuttle', 'run'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2
        assert output.find("No tuttlefile") >= 0

    def test_tuttle_file_does_not_exist(self):
        """ Should display a message if the tuttlefile passed as argument to the command line does not exist"""
        proc = Popen(['tuttle', 'run', '-f', 'inexistant_file' ], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2
        assert output.find("No tuttlefile") >= 0
