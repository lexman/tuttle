# -*- coding: utf8 -*-

from tests.functional_tests import isolate, run_tuttle_file
import sqlite3
import shutil
from os import path, getcwd


class TestSQLiteResource():

    # def test_parse_url(self):
    #     """A real resource should exist"""
    #     url = "sqlite://relative/path/to/sqlite_file/tables/mytable"
    #     res = SQLiteResource(url)
    #     assert res.db_file == "relative/path/to/sqlite_file"
    #     assert res.table == "mytable"
    #
    # def test_sqlite_file_does_not_exists(self):
    #     """Event the sqlite file does not exits"""
    #     url = "sqlite://unknonw_sqlite_file/tables/mytable"
    #     res = SQLiteResource(url)
    #     assert res.exists() == False
    #
    # @isolate(['tests.sqlite'])
    # def test_sqlite_table_does_not_exists(self):
    #     """The sqlite file exists but the tabble doesn't"""
    #     url = "sqlite://tests.sqlite/tables/unknown_test_table"
    #     res = SQLiteResource(url)
    #     assert res.exists() == False
    #
    # @isolate(['tests.sqlite'])
    # def test_sqlite_table_exists(self):
    #     """exists() should return True when the table exists"""
    #     url = "sqlite://tests.sqlite/tables/test_table"
    #     res = SQLiteResource(url)
    #     assert res.exists()
    #
    # @isolate(['tests.sqlite'])
    # def test_remove_table(self):
    #     """exists() should return True when the table exists"""
    #     url = "sqlite://tests.sqlite/tables/test_table"
    #     res = SQLiteResource(url)
    #     assert res.exists()
    #     res.remove()
    #     assert not res.exists()
    #
    # def test_sqlite_processor_should_be_availlable(self):
    #     """A project with an SQLite processor should be Ok"""
    #     project = "sqlite://db.sqlite/tables/my_table <- sqlite://db.sqlite/tables/my_table ! sqlite"
    #     pp = ProjectParser()
    #     pp.set_project(project)
    #     pp.read_line()
    #     process = pp.parse_dependencies_and_processor()
    #     assert process._processor.name == "sqlite"
    #
    # def test_sqlite_pre_check_ok_with_no_outputs(self):
    #     """Pre-check should work even if there are no outputs"""
    #     project = " <- sqlite://db.sqlite/tables/my_table ! sqlite"
    #     pp = ProjectParser()
    #     pp.set_project(project)
    #     pp.read_line()
    #     process = pp.parse_dependencies_and_processor()
    #     assert process._processor.name == "sqlite"
    #     process.pre_check()
    #
    # def test_sqlite_pre_check_ok_with_no_inputs(self):
    #     """Pre-check should work even if there are no inputs"""
    #     project = "sqlite://db.sqlite/tables/my_table <- ! sqlite"
    #     pp = ProjectParser()
    #     pp.set_project(project)
    #     pp.read_line()
    #     process = pp.parse_dependencies_and_processor()
    #     assert process._processor.name == "sqlite"
    #     process.pre_check()
    #
    # def test_sqlite_pre_check_should_fail_without_sqlite_resources(self):
    #     """Pre-check should fail if no SQLiteResources are specified either in inputs or outputs"""
    #     project = "<- ! sqlite"
    #     pp = ProjectParser()
    #     pp.set_project(project)
    #     pp.read_line()
    #     process = pp.parse_dependencies_and_processor()
    #     assert process._processor.name == "sqlite"
    #     try:
    #         process.pre_check()
    #         assert False, "Pre-check should not have allowed SQLIteProcessor without SQLiteResources"
    #     except SQLiteTuttleError:
    #         assert True

    @isolate(['test.csv'])
    def test_sqlite_processor(self):
        """A project with an SQLite processor should run the sql statements"""
        project = """sqlite://db.sqlite/tables/pop <- file://test.csv ! csv2sqlite
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        with sqlite3.connect('db.sqlite') as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM pop")
            expected = u"""Aruba,ABW,102911
Andorra,AND,79218
Afghanistan,AFG,30551674
Angola,AGO,21471618
Albania,ALB,2897366
Arab World,ARB,369762523
United Arab Emirates,ARE,9346129""".split("\n")

            for exp in expected:
                a_result = cur.next()
                assert a_result == tuple(exp.split(','))
            try:
                cur.next()
                assert False, "Detected an extra line on the table"
            except:
                assert True

    @isolate(['bad_csv.csv'])
    def test_bad_csv__should_fail_with_csv_2sqlite(self):
        """ A csv without the good number of columns in one raw should make the process fail"""
        project = """sqlite://db.sqlite/tables/pop <- file://bad_csv.csv ! csv2sqlite
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2, output
        assert output.find("Wrong number of columns on line 4")>= 0

    def assertF(self, output, truc):
        assert False, output

    @isolate(['test_csv.py'])
    def test_text_file_should_fail_with_csv_2sqlite(self):
        """ A source file that is not a csv should make the process fail"""
        project = """sqlite://db.sqlite/tables/pop <- file://test_csv.py ! csv2sqlite
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2, output
        error_text_found = output.find("Wrong")>= 0
        error_text_found = error_text_found or output.find("Is this file a valid CSV file ?") >= 0
        assert error_text_found, output

    @isolate(['tests.sqlite'])
    def test_binary_file_should_fail_with_csv_2sqlite(self):
        """ A binary file that is not a csv should make the process fail"""
        project = """sqlite://db.sqlite/tables/pop <- file://tests.sqlite ! csv2sqlite
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2, output
        assert output.find("Is this file a valid CSV file ?")>= 0, output

    # @isolate(['tests.sqlite'])
    # def test_sql_error_in_sqlite_processor(self):
    #     """ If an error occurs, tuttle should fail and output logs should trace the error"""
    #     project = """sqlite://tests.sqlite/tables/new_table <- sqlite://tests.sqlite/tables/test_table ! sqlite
    #     CREATE TABLE new_table AS SELECT * FROM test_table;
    #
    #     NOT an SQL statement;
    #     """
    #     rcode, output = run_tuttle_file(project)
    #     assert rcode == 2
    #     error_log = open(join('.tuttle', 'processes', 'logs', 'sqlite_1_err')).read()
    #     assert error_log.find('near "NOT": syntax error') >= 0, error_log
    #
