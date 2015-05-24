
# -*- coding: utf8 -*-
from os.path import join, isfile
from tests.functional_tests import isolate, run_tuttle_file
from tuttle.extensions.sqlite import SQLiteResource, SQLiteTuttleError
from tuttle.project_parser import ProjectParser


class TestPythonProcessor():

    def test_python_processor_should_be_availlable(self):
        """A project with an python processor should be Ok"""
        project = "file://B <- file://A ! python"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "python"


    @isolate(['A'])
    def test_python_processor(self):
        """A project with an SQLite processor should run the sql statements"""
        project = """file://B <- file://A ! python
        # -*- coding: utf8 -*-

        from time import time
        print("A python process at {}".format(time()))
        open('B', 'w').write('A produces B')
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("A python process") >= 0


    @isolate(['A'])
    def test_error_in_python_processor(self):
        """ If an error occurs, tuttle should fail and output logs should trace the error"""
        project = """file://B <- file://A ! python
        # -*- coding: utf8 -*-

        open('B', 'w').write('A produces B')
        a = 0
        print("should raise an error : {}".format(0 / a))
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2
        error_log = open(join('.tuttle', 'processes', 'logs', 'tuttlefile_1_err')).read()
        assert error_log.find('ZeroDivisionError:') >= 0, error_log

    # @isolate(['tests.sqlite'])
    # def test_comments_in_process(self):
    #     """ If an error occurs, tuttle should fail and output logs should trace the error"""
    #     project = """sqlite://tests.sqlite/tables/new_table <- sqlite://tests.sqlite/tables/test_table ! sqlite
    #     CREATE TABLE new_table AS SELECT * FROM test_table;
    #     -- This is a comment
    #     /* last comment style*/
    #     """
    #     rcode, output = run_tuttle_file(project)
    #     error_log = open(join('.tuttle', 'processes', 'logs', 'tuttlefile_1_err')).read()
    #     assert rcode == 0, error_log
    #     assert output.find("comment") >= 0
