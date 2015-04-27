# -*- coding: utf8 -*-
from os.path import join, isfile
from tests.functional_tests import isolate, run_tuttle_file
from tuttle.extensions.sqlite import SQLiteResource, SQLiteTuttleError
from tuttle.project_parser import ProjectParser


class TestSQLiteResource():

    def test_parse_url(self):
        """A real resource should exist"""
        url = "sqlite://relative/path/to/sqlite_file/tables/mytable"
        res = SQLiteResource(url)
        assert res.db_file == "relative/path/to/sqlite_file"
        assert res.table == "mytable"

    def test_sqlite_file_does_not_exists(self):
        """Event the sqlite file does not exits"""
        url = "sqlite://unknonw_sqlite_file/tables/mytable"
        res = SQLiteResource(url)
        assert res.exists() == False

    @isolate(['tests.sqlite'])
    def test_sqlite_table_does_not_exists(self):
        """The sqlite file exists but the tabble doesn't"""
        url = "sqlite://tests.sqlite/tables/unknown_test_table"
        res = SQLiteResource(url)
        assert res.exists() == False

    @isolate(['tests.sqlite'])
    def test_sqlite_table_exists(self):
        """exists() should return True when the table exists"""
        url = "sqlite://tests.sqlite/tables/test_table"
        res = SQLiteResource(url)
        assert res.exists()

    @isolate(['tests.sqlite'])
    def test_remove_table(self):
        """exists() should return True when the table exists"""
        url = "sqlite://tests.sqlite/tables/test_table"
        res = SQLiteResource(url)
        assert res.exists()
        res.remove()
        assert not res.exists()

    def test_sqlite_processor_should_be_availlable(self):
        """A project with an SQLite processor should be Ok"""
        project = "sqlite://db.sqlite/tables/my_table <- sqlite://db.sqlite/tables/my_table #! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"

    def test_pre_check_should_fail_if_across_several_sqlite_files(self):
        """Pre-check should fail for SQLite processor if it is supposed to work with several SQLite files"""
        project = "sqlite://db1.sqlite/tables/my_table <- sqlite://db2.sqlite/tables/my_table #! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"
        try:
            process.pre_check()
            assert False, "Pre-check should not have allowed to sqlite files"
        except SQLiteTuttleError:
            assert True

    def test_sqlite_pre_check_ok_with_no_outputs(self):
        """Pre-check should work even if there are no outputs"""
        project = " <- sqlite://db.sqlite/tables/my_table #! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"
        process.pre_check()

    def test_sqlite_pre_check_ok_with_no_inputs(self):
        """Pre-check should work even if there are no inputs"""
        project = "sqlite://db.sqlite/tables/my_table <- #! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"
        process.pre_check()

    def test_sqlite_pre_check_should_fail_without_sqlite_resources(self):
        """Pre-check should fail if no SQLiteResources are specified either in inputs or outputs"""
        project = "<- #! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"
        try:
            process.pre_check()
            assert False, "Pre-check should not have allowed SQLIteProcessor without SQLiteResources"
        except SQLiteTuttleError:
            assert True

    @isolate(['tests.sqlite'])
    def test_sqlite_processor(self):
        """A project with an SQLite processor should run the sql statements"""
        project = """sqlite://tests.sqlite/tables/new_table <- sqlite://tests.sqlite/tables/test_table #! sqlite
        CREATE TABLE new_table AS SELECT * FROM test_table;
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("CREATE TABLE new_table AS SELECT * FROM test_table"), \
            "SQLiteProcessor should log the SQL statements"

    @isolate(['tests.sqlite'])
    def test_sqlite_processor_with_several_instuctions(self):
        """ An SQLiteProcess can have several SQL instructions"""
        project = """sqlite://tests.sqlite/tables/new_table, sqlite://tests.sqlite/tables/another_table  <- sqlite://tests.sqlite/tables/test_table #! sqlite
        CREATE TABLE new_table AS SELECT * FROM test_table;

        CREATE TABLE another_table (id int, col1 string);
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

    @isolate(['tests.sqlite'])
    def test_sql_error_in_sqlite_processor(self):
        """ If an error occurs, tuttle should fail and output logs should trace the error"""
        project = """sqlite://tests.sqlite/tables/new_table <- sqlite://tests.sqlite/tables/test_table #! sqlite
        CREATE TABLE new_table AS SELECT * FROM test_table;

        NOT an SQL statement;
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2
        error_log = open(join('.tuttle', 'processes', 'logs', 'tuttlefile_1_err')).read()
        assert error_log.find('near "NOT": syntax error') >= 0, error_log

    @isolate(['tests.sqlite'])
    def test_comments_in_process(self):
        """ If an error occurs, tuttle should fail and output logs should trace the error"""
        project = """sqlite://tests.sqlite/tables/new_table <- sqlite://tests.sqlite/tables/test_table #! sqlite
        CREATE TABLE new_table AS SELECT * FROM test_table;
        -- This is a comment
        /* last comment style*/
        """
        rcode, output = run_tuttle_file(project)
        error_log = open(join('.tuttle', 'processes', 'logs', 'tuttlefile_1_err')).read()
        assert rcode == 0, error_log
        assert output.find("comment") >= 0

    @isolate(['tests.sqlite'])
    def test_sqlite_file_should_be_deleted_if_empty_after_remove(self):
        """ When an SQLiteResource is removed, the sqlite file should be delete if it is empty """
        url = "sqlite://tests.sqlite/tables/test_table"
        res = SQLiteResource(url)
        assert res.exists()
        assert isfile("tests.sqlite")
        res.remove()
        assert not res.exists()
        assert not isfile("tests.sqlite")

    @isolate(['tests.sqlite'])
    def test_sqlite_file_should_not_be_deleted_if_not_empty_after_remove(self):
        """ When an SQLiteResource is removed, then sqlite file should be not delete if it is not empty """
        project = """sqlite://tests.sqlite/tables/to_be_removed <- #! sqlite
        CREATE TABLE to_be_removed AS SELECT * FROM test_table;
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0
        # The table exists !
        url = "sqlite://tests.sqlite/tables/to_be_removed"
        res = SQLiteResource(url)
        assert isfile("tests.sqlite")
        res.remove()
        assert not res.exists()
        assert isfile("tests.sqlite")
