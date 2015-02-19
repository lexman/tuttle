# -*- coding: utf-8 -*-

from unittest import TestCase
from subprocess import check_output
from os import getcwd, chdir, remove
from shutil import rmtree
from os import path


class FunctionalTestBase(TestCase):

    def write_tuttlefile(self, content):
        with open('tuttlefile', "w") as f:
            f.write(content)

    def run_tuttle(self):
        return check_output(['python', self._tuttle_cmd])

    def _rm(self, filename):
        if path.isdir(filename):
            rmtree('.tuttle')
        elif path.isfile(filename):
            remove(filename)

    def reset(self):
        self._rm('tuttlefile')
        self._rm('tuttle_report.html')
        self._rm('.tuttle')

    def setUp(self):
        self._cwd = getcwd()
        dirname = path.dirname(__file__)
        self._tuttle_cmd = path.abspath(path.join(dirname, '..', '..', 'bin', 'tuttle'))

    def work_dir_from_module(self, filename):
        dirname = path.dirname(filename)
        chdir(dirname)
        self.reset()

    def tearDown(self):
        self.reset()
        chdir(self._cwd)
