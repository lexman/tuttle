# -*- coding: utf-8 -*-
from tempfile import mkdtemp

from unittest import TestCase
from subprocess import check_output
from os import getcwd, chdir, remove
from shutil import rmtree, copy
from os import path
from functools import wraps
from os.path import basename, join, dirname


def isolate(arg):
    if isinstance(arg, list):
        files = arg
    elif callable(arg):
        files = []

    def wrap(func):
        funct_dir = dirname(func.func_globals['__file__'])

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            tmp_dir = mkdtemp()
            for filename in files:
                src = join(funct_dir, filename)
                dst = join(tmp_dir, filename)
                copy(src, dst)
            cwd = getcwd()
            chdir(tmp_dir)
            try:
                return func(*args, **kwargs)
            finally:
                chdir(cwd)
                rmtree(tmp_dir)
        return wrapped_func
    if isinstance(arg, list):
        return wrap
    elif callable(arg):
        return wrap(arg)


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
