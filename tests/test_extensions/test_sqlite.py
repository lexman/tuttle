# -*- coding: utf8 -*-
from os.path import join, isfile
from tests.functional_tests import isolate, run_tuttle_file
from tuttle.extensions.sqlite import SQLiteResource, SQLiteTuttleError
from tuttle.project_parser import ProjectParser


class TestSQLiteResource():

    def test_parse_url(self):
        """A real resource should exist"""
        url = "sqlite://relative/path/to/sqlite_file/mytable"
        res = SQLiteResource(url)
        assert res.db_file == "relative/path/to/sqlite_file"
        assert res.table == "mytable"

    def test_sqlite_file_does_not_exists(self):
        """Event the sqlite file does not exits"""
        url = "sqlite://unknonw_sqlite_file/mytable"
        res = SQLiteResource(url)
        assert res.exists() == False

    @isolate(['tests.sqlite'])
    def test_sqlite_table_does_not_exists(self):
        """The sqlite file exists but the tabble doesn't"""
        url = "sqlite://tests.sqlite/unknown_test_table"
        res = SQLiteResource(url)
        assert res.exists() == False

    @isolate(['tests.sqlite'])
    def test_sqlite_table_exists(self):
        """exists() should return True when the table exists"""
        url = "sqlite://tests.sqlite/test_table"
        res = SQLiteResource(url)
        assert res.exists()

    @isolate(['tests.sqlite'])
    def test_remove_table(self):
        """exists() should return True when the table exists"""
        url = "sqlite://tests.sqlite/test_table"
        res = SQLiteResource(url)
        assert res.exists()
        res.remove()
        assert not res.exists()

    def test_sqlite_processor_should_be_availlable(self):
        """A project with an SQLite processor should be Ok"""
        project = "sqlite://db.sqlite/my_table <- sqlite://db.sqlite/my_table ! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"

    def test_static_check_should_fail_if_across_several_sqlite_files(self):
        """Static check should fail for SQLite processor if it is supposed to work with several SQLite files"""
        project = "sqlite://db1.sqlite/my_table <- sqlite://db2.sqlite/my_table ! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"
        try:
            process.static_check()
            assert False, "Static check should not have allowed to sqlite files"
        except SQLiteTuttleError:
            assert True

    def test_sqlite_static_check_ok_with_no_outputs(self):
        """static check should work even if there are no outputs"""
        project = " <- sqlite://db.sqlite/my_table ! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"
        process.static_check()

    def test_sqlite_static_check_ok_with_no_inputs(self):
        """Static check should work even if there are no inputs"""
        project = "sqlite://db.sqlite/my_table <- ! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"
        process.static_check()

    def test_sqlite_static_check_should_fail_without_sqlite_resources(self):
        """Static check should fail if no SQLiteResources are specified either in inputs or outputs"""
        project = "<- ! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"
        try:
            process.static_check()
            assert False, "Static check should not have allowed SQLIteProcessor without SQLiteResources"
        except SQLiteTuttleError:
            assert True

    @isolate(['tests.sqlite'])
    def test_sqlite_processor(self):
        """A project with an SQLite processor should run the sql statements"""
        project = """sqlite://tests.sqlite/new_table <- sqlite://tests.sqlite/test_table ! sqlite
        CREATE TABLE new_table AS SELECT * FROM test_table;
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("CREATE TABLE new_table AS SELECT * FROM test_table"), \
            "SQLiteProcessor should log the SQL statements"

    @isolate(['tests.sqlite'])
    def test_sqlite_processor_with_several_instuctions(self):
        """ An SQLiteProcess can have several SQL instructions"""
        project = """sqlite://tests.sqlite/new_table, sqlite://tests.sqlite/another_table  <- sqlite://tests.sqlite/test_table ! sqlite
        CREATE TABLE new_table AS SELECT * FROM test_table;

        CREATE TABLE another_table (id int, col1 string);
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

    @isolate(['tests.sqlite'])
    def test_sql_error_in_sqlite_processor(self):
        """ If an error occurs, tuttle should fail and output logs should trace the error"""
        project = """sqlite://tests.sqlite/new_table <- sqlite://tests.sqlite/test_table ! sqlite
        CREATE TABLE new_table AS SELECT * FROM test_table;

        NOT an SQL statement;
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2
        error_log = open(join('.tuttle', 'processes', 'logs', 'tuttlefile_1_err.txt')).read()
        assert error_log.find('near "NOT": syntax error') >= 0, error_log

    @isolate(['tests.sqlite'])
    def test_comments_in_process(self):
        """ If an error occurs, tuttle should fail and output logs should trace the error"""
        project = """sqlite://tests.sqlite/new_table <- sqlite://tests.sqlite/test_table ! sqlite
        CREATE TABLE new_table AS SELECT * FROM test_table;
        -- This is a comment
        /* last comment style*/
        """
        rcode, output = run_tuttle_file(project)
        error_log = open(join('.tuttle', 'processes', 'logs', 'tuttlefile_1_err.txt')).read()
        assert rcode == 0, error_log
        assert output.find("comment") >= 0

    @isolate(['tests.sqlite'])
    def test_sqlite_file_should_be_deleted_if_empty_after_last_remove(self):
        """ When an SQLiteResource is removed, the sqlite file should be delete if it is empty """
        url1 = "sqlite://tests.sqlite/test_table_not_empty"
        res1 = SQLiteResource(url1)
        assert res1.exists()
        assert isfile("tests.sqlite")
        res1.remove()
        assert not res1.exists()
        assert isfile("tests.sqlite")
        url2 = "sqlite://tests.sqlite/test_table"
        res2 = SQLiteResource(url2)
        assert res2.exists()
        res2.remove()
        assert not res2.exists()
        assert not isfile("tests.sqlite")

    @isolate(['tests.sqlite'])
    def test_sqlite_file_should_not_be_deleted_if_not_empty_after_remove(self):
        """ When an SQLiteResource is removed, then sqlite file should be not delete if it is not empty """
        project = """sqlite://tests.sqlite/to_be_removed <- ! sqlite
        CREATE TABLE to_be_removed AS SELECT * FROM test_table;
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0
        # The table exists !
        url = "sqlite://tests.sqlite/to_be_removed"
        res = SQLiteResource(url)
        assert isfile("tests.sqlite")
        res.remove()
        assert not res.exists()
        assert isfile("tests.sqlite")

    @isolate(['tests.sqlite'])
    def test_sqlite_empty_table_signature(self):
        """signature() should return a hash of the structure for an empty table"""
        url = "sqlite://tests.sqlite/test_table"
        res = SQLiteResource(url)
        sig = res.signature()
        expected = "d2281930bd11c54226395064b10cb3e5f6931ea3"
        assert sig == expected, sig

    @isolate(['tests.sqlite'])
    def test_sqlite_empty_table_signature(self):
        """signature() should return a hash of the structure and the data for a table"""
        url = "sqlite://tests.sqlite/test_table_not_empty"
        res = SQLiteResource(url)
        sig = res.signature()
        expected = "3ee7b386c4daed31a7d57fbb0fd32c482c7be1d1"
        assert sig == expected, sig

#    @isolate(['tests.sqlite'])
#    def test_sqlite_index_exists(self):
#        """exists() should return True when the index exists"""
#        url = "sqlite://tests.sqlite/indexes/test_table"
#        res = SQLiteResource(url)
#        assert(res.exists(), "{} should exist".format(url))

#    @isolate(['tests.sqlite'])
#    def test_sqlite_inexistant_index_do_not_exists(self):
#        """exists() should return False when the index does not exists"""
#        url = "sqlite://tests.sqlite/indexes/inexistant_index"
#        res = SQLiteResource(url)
#        assert(res.exists(), "{} should not exist".format(url))

    # TODO test a table with space in name