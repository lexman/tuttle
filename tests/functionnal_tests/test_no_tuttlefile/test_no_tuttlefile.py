#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tuttle.project_parser import *
from subprocess import check_output
from os import getcwd, chdir, remove, rmdir
from shutil import rmtree
from os import path


def write_tuttlefile(content):
    with open('tuttlefile', "w") as f:
        f.write(content)

def run_tuttle():
    return check_output(['python', path.join('..', '..', '..', 'bin', 'tuttle')], shell=True)

def rm(filename):
    if path.isdir(filename):
        rmtree('.tuttle')
    elif path.isfile(filename):
        remove(filename)

def raz():
    rm('tuttlefile')
    rm('last_workflow.pickle')
    rm('report.html')
    rm('workflow.dot')
    rm('.tuttle')


class TestNoTuttlefile():

    def test_no_file_in_current_dir(self):
        """ Should display a message if there is no tuttlefile in the current directory"""
        cwd = getcwd()
        dirname = path.dirname(__file__)
        try:
            chdir(dirname)
            result = run_tuttle()
            assert result.find("No tuttlefile") >= 0
        finally:
            raz()
            chdir(cwd)


    def test_tuttle_file_does_not_exist(self):
        """ Should display a message if the tuttlefile passed as argument to the command line does not exist"""
        result = check_output(['python', path.join('bin', 'tuttle'), '-p', 'inexistant_file'], shell=True)
        assert result.find("No tuttlefile") >= 0
        raz()
