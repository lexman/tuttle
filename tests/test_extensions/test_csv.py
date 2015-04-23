# -*- coding: utf8 -*-

from tests.functional_tests import isolate, run_tuttle_file
import sqlite3


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
    #     project = "sqlite://db.sqlite/tables/my_table <- sqlite://db.sqlite/tables/my_table #! sqlite"
    #     pp = ProjectParser()
    #     pp.set_project(project)
    #     pp.read_line()
    #     process = pp.parse_dependencies_and_processor()
    #     assert process._processor.name == "sqlite"
    #
    # def test_sqlite_pre_check_ok_with_no_outputs(self):
    #     """Pre-check should work even if there are no outputs"""
    #     project = " <- sqlite://db.sqlite/tables/my_table #! sqlite"
    #     pp = ProjectParser()
    #     pp.set_project(project)
    #     pp.read_line()
    #     process = pp.parse_dependencies_and_processor()
    #     assert process._processor.name == "sqlite"
    #     process.pre_check()
    #
    # def test_sqlite_pre_check_ok_with_no_inputs(self):
    #     """Pre-check should work even if there are no inputs"""
    #     project = "sqlite://db.sqlite/tables/my_table <- #! sqlite"
    #     pp = ProjectParser()
    #     pp.set_project(project)
    #     pp.read_line()
    #     process = pp.parse_dependencies_and_processor()
    #     assert process._processor.name == "sqlite"
    #     process.pre_check()
    #
    # def test_sqlite_pre_check_should_fail_without_sqlite_resources(self):
    #     """Pre-check should fail if no SQLiteResources are specified either in inputs or outputs"""
    #     project = "<- #! sqlite"
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
        project = """sqlite://db.sqlite/tables/pop <- csv://test.csv #! csv2sqlite
        """
        rcode, output = run_tuttle_file(project)
        print output
        assert rcode == 0, output
        db = sqlite3.connect('db.sqlite')
        cur = db.cursor()
        all = cur.fetchall()
        assert False, all


    # @isolate(['tests.sqlite'])
    # def test_sql_error_in_sqlite_processor(self):
    #     """ If an error occurs, tuttle should fail and output logs should trace the error"""
    #     project = """sqlite://tests.sqlite/tables/new_table <- sqlite://tests.sqlite/tables/test_table #! sqlite
    #     CREATE TABLE new_table AS SELECT * FROM test_table;
    #
    #     NOT an SQL statement;
    #     """
    #     rcode, output = run_tuttle_file(project)
    #     assert rcode == 2
    #     error_log = open(join('.tuttle', 'processes', 'logs', 'sqlite_1_err')).read()
    #     assert error_log.find('near "NOT": syntax error') >= 0, error_log
    #
