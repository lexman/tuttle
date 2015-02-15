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


class TestProjectParser():

    def test_remove_resource(self):
        """If a resource is removed from a tuttlefile, it should be deleted"""
        cwd = getcwd()
        dirname = path.dirname(__file__)
        try:
            chdir(dirname)
            raz()
            first = """file://B <- file://A
        echo A produces B
        echo B > B

file://C <- file://B
        echo B produces C
        echo C > C

file://D <- file://A
        echo A produces D
        echo D > D
"""
            write_tuttlefile(first)
            result = run_tuttle()
            assert path.exists('B')
            assert path.exists('C')
            assert path.exists('D')
            second = """file://C <- file://A
    echo A produces C
    echo C > C

file://D <- file://A
    echo A produces D
    echo D > D
"""
            write_tuttlefile(second)
            result = run_tuttle()
            assert result.find("* file://B") >= 0
            assert result.find("* file://C") >= 0
            print result
        finally:
            raz()
            rm('B')
            rm('C')
            rm('D')
            chdir(cwd)

