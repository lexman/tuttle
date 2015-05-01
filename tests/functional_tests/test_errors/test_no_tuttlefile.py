# -*- coding: utf-8 -*-

from subprocess import check_output, Popen, PIPE
from os.path import abspath, join, dirname
from tests.functional_tests import isolate


class TestNoTuttlefile():

    @isolate
    def test_no_file_in_current_dir(self):
        """ Should display a message if there is no tuttlefile in the current directory"""
        dir = dirname(__file__)
        #tuttle_cmd = abspath(join(dir, '..', '..', '..', 'bin', 'tuttle'))
        tuttle_cmd = abspath(join(dir, '..', '..', '..', 'tuttle.py'))
        proc = Popen(['python', tuttle_cmd], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2
        assert output.find("No tuttlefile") >= 0


    def test_tuttle_file_does_not_exist(self):
        """ Should display a message if the tuttlefile passed as argument to the command line does not exist"""
        dir = dirname(__file__)
        tuttle_cmd = abspath(join(dir, '..', '..', '..', 'bin', 'tuttle'))
        tuttle_cmd = abspath(join(dir, '..', '..', '..', 'tuttle.py'))
        proc = Popen(['python', tuttle_cmd, '-f', 'inexistant_file'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2
        assert output.find("No tuttlefile") >= 0
