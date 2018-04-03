# -*- coding: utf8 -*-
from os.path import join

import psycopg2

from tests.functional_tests import run_tuttle_file, isolate
from tuttle.addons.odbc import ODBCResource
from tuttle.addons.postgres import PostgreSQLResource, PostgresqlTuttleError
from nose.plugins.skip import SkipTest

from tuttle.commands import run
from tuttle.error import TuttleError
from tuttle.project_parser import ProjectParser
from tuttle.resource import MalformedUrl


class TestODBCResource():
    """
    Test tuttle with ODBC resources
    To ensure tests will be run, you must provide access to a local ODBC database with DSN called tuttle_test_db,
    To ensure tests will be run, you must provide access to a local postgresql database called tuttle_test_db,


    then you must run the tests with environment variables allowing access to this database.
    Eg, if you have defined a user tuttle with password tuttle, you can run the tests like this on Linux :
        export PGUSER=tuttle
        export PGPASSWORD=tuttle
        nosetests
    """

    __test_dsn = "tuttle_test_db"

    def setUp(self):
        try:
            import pyodbc
            conn_string = "dsn={}".format(self.__test_dsn)
            conn = pyodbc.connect(conn_string)

        except pyodbc.InterfaceError:
            raise SkipTest("No ODBC database configured to run the tests")
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS test_table_project CASCADE")
        cur.execute("DROP TABLE IF EXISTS test_table CASCADE")
        cur.execute("DROP TABLE IF EXISTS test_partitionned_table CASCADE")
        cur.execute("DROP TABLE IF EXISTS test_partitionned_table_num CASCADE")
        cur.execute("CREATE TABLE test_table (col1 INT)")
        cur.execute("INSERT INTO test_table (col1) VALUES (12)")
        cur.execute("CREATE TABLE test_partitionned_table (col1 TEXT)")
        cur.execute("INSERT INTO test_partitionned_table (col1) VALUES ('val1')")
        cur.execute("CREATE TABLE test_partitionned_table_num (col_int INT, col_float FLOAT)")
        cur.execute("INSERT INTO test_partitionned_table_num (col_int, col_float) VALUES (14, 3.14)")
        cur.execute("INSERT INTO test_partitionned_table_num (col_int, col_float) VALUES (42, 2.72)")
        #cur.execute("DROP VIEW IF EXISTS test_view")
        #cur.execute("CREATE VIEW test_view AS SELECT * FROM test_table")
        conn.commit()

    def test_parse_standard_url(self):
        """A standard odbc url should provide a valid resource"""
        url = "odbc://tuttle_test_db/test_table"
        res = ODBCResource(url)
        assert res._dsn == "tuttle_test_db", res._dsn
        assert res._relation == "test_table", res._table

    def test_odbc_table_exists(self):
        """exists() should return True when the table exists"""
        url = "odbc://tuttle_test_db/test_table"
        res = ODBCResource(url)
        assert res.exists(), "{} should exist".format(url)

    def test_odbc_table_not_exists(self):
        """the table should not exist"""
        url = "odbc://tuttle_test_db/no_table"
        res = ODBCResource(url)
        assert not res.exists(), "{} should exist".format(url)

    def test_remove_table(self):
        """remove() should remove a table"""
        url = "odbc://tuttle_test_db/test_table"
        res = ODBCResource(url)
        assert res.exists(), "{} should exist".format(url)
        res.remove()
        assert not res.exists(), "{} should not exist".format(url)

    def test_remove_partition(self):
        """remove() should remove a table"""
        partition_to_delete = "odbc://tuttle_test_db/test_partitionned_table_num?col_int=14"
        resource_to_delete = ODBCResource(partition_to_delete)
        assert resource_to_delete.exists(), "{} should exist".format(partition_to_delete)
        other_partition = "odbc://tuttle_test_db/test_partitionned_table_num?col_int=42"
        other_resource = ODBCResource(other_partition)
        assert resource_to_delete.exists(), "{} should exist".format(other_partition)
        resource_to_delete.remove()
        assert not resource_to_delete.exists(), "{} should not exist anymore".format(partition_to_delete)
        assert other_resource.exists(), "Other partition {} should still exist".format(other_partition)

    def test_table_signature(self):
        """signature() should return a hash of the structure and the data for a table"""
        url = "odbc://tuttle_test_db/test_table"
        res = ODBCResource(url)
        sig = res.signature()
        expected = "7b52009b64fd0a2a49e6d8a939753077792b0554"
        assert sig == expected, sig

    def test_partition_signature(self):
        """signature() should return a hash of the structure and the data for a table"""
        url = "odbc://tuttle_test_db/test_partitionned_table_num?col_int=14"
        res = ODBCResource(url)
        sig = res.signature()
        expected = "d22e04365ffe5ba05d7f5ec4f2115fde8d251e3d"
        assert sig == expected, sig

#    def test_odbc_view_exists(self):
#        """exists() should return True when the table exists"""
#        url = "odbc://tuttle_test_db/test_view"
#        res = ODBCResource(url)
#        assert res.exists(), "{} should exist".format(url)

    def test_parse_partitionned_url(self):
        """A standard odbc url should provide a valid resource"""
        url = "odbc://tuttle_test_db/test_partitionned_table?col1=val1"
        res = ODBCResource(url)
        assert res._dsn == "tuttle_test_db", res._dsn
        assert res._relation == "test_partitionned_table", res._relation
        assert "col1" in res._filters, res._filters
        assert res._filters["col1"] == "val1", res._filters["col1"]

    def test_parse_too_many_values_in_filter(self):
        """Should raise if url contains several times the same filter"""
        url = "odbc://tuttle_test_db/test_partitionned_table?col1=val1&col1=val2"
        try:
            res = ODBCResource(url)
            assert False, "Should have raised"
        except MalformedUrl as e:
            assert e.message.find("Too many values")

    def test_odbc_table_partition_exists(self):
        """exists() should return True when a partition exists in the table"""
        url = "odbc://tuttle_test_db/test_partitionned_table?col1=val1"
        res = ODBCResource(url)
        assert res.exists(), "{} should exist".format(url)

    def test_odbc_table_partition_exists_with_int(self):
        """exists() should return True when a partition exists in the table"""
        url = "odbc://tuttle_test_db/test_partitionned_table_num?col_int=14"
        res = ODBCResource(url)
        assert res.exists(), "{} should exist".format(url)

    def test_odbc_table_partition_does_not_exists_with_int(self):
        """exists() should return True when a partition exists in the table"""
        url = "odbc://tuttle_test_db/test_partitionned_table_num?col_int=13"
        res = ODBCResource(url)
        assert not res.exists(), "{} should not exist".format(url)

    def test_odbc_table_partition_not_exists(self):
        """exists() should return False if there are no data in the partition"""
        url = "odbc://tuttle_test_db/test_partitionned_table?col1=unknown_value"
        res = ODBCResource(url)
        assert not res.exists(), "{} should not exist".format(url)

    def test_odbc_partition_raise_if_table_not_exists(self):
        """exists() for a partition should raise if the table does not exist"""
        url = "odbc://tuttle_test_db/no_table?col1=val1"
        res = ODBCResource(url)
        try:
            res.exists()
            assert False, "Should have raised because the table does not exists"
        except TuttleError as e:
            assert True

    def test_bad_dsn(self):
        """If DSN does not exist, should tell tuttle can't connect !"""
        url = "odbc://unknown_dsn/test_table"
        res = ODBCResource(url)
        try:
            res.exists()
            assert False
        except TuttleError as e:
            assert e.message.find("to check existence of resource") > 0, e.message

    @isolate
    def test_odbc_resources_are_available_in_tuttle(self):
        """A project with an odbc resource should be valid"""
        project = """odbc://tuttle_test_db/test_table_project <- ! python
            import pyodbc
            conn_string = "dsn=tuttle_test_db"
            db = pyodbc.connect(conn_string)
            cur=db.cursor()
            cur.execute("CREATE TABLE test_table_project (col INT)")
            db.commit()
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("Done") >= 0, output

    def test_cant_connect(self):
        """ Should display a message if tuttle cant connect to database """
        project = """odbc://this_dsn_does_not_exists/table <- ! python
            import pyodbc
            conn_string = "dsn=this_dsn_does_not_exists"
            db = pyodbc.connect(conn_string)
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2, output
        assert output.find("Can't connect")> -1, output

    @isolate
    def test_odbc_partitioned_url_in_project(self):
        """partitionned url should not raise (from utf8 bug)"""
        # parse_qs needs an ascii string,
        # and auto mapping of values fails with utf8
        project = """odbc://tuttle_test_db/test_partitionned_table_num?col_int=14 <- ! odbc"""
        rcode, output = run_tuttle_file(project)

    @isolate
    def test_odbc_partition_cant_overlap(self):
        """There can be only one partition for a table"""
        project = """odbc://tuttle_test_db/test_partitionned_table_num?col_int=14 <- ! odbc
            INSERT INTO test_partitionned_table_num (col_int, col_float) VALUES (14, 3.14)
        
odbc://tuttle_test_db/test_partitionned_table_num?col_float=3.14 <- ! odbc
            INSERT INTO test_partitionned_table_num (col_int, col_float) VALUES (14, 3.14)
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 2, output
        assert output.find("overlap") >= 0, output

    @isolate
    def test_primary_odbc_partition_can_overlap(self):
        """ If the partition is a primary, it can overlap """
        project = """<- odbc://tuttle_test_db/test_partitionned_table_num?col_int=14 ! odbc
            SELECT * FROM test_partitionned_table_num WHERE col_int=14

odbc://tuttle_test_db/test_partitionned_table_num?col_float=3.14 <- ! odbc
            INSERT INTO test_partitionned_table_num (col_int, col_float) VALUES (14, 3.14)
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output


class TestODBCProcessor():
    """
    Test the odbc processor
    To ensure tests will be run, you must provide access to a local postgresql database called tuttle_test_db,
    that will be exposed as ODBC
    To be able to run the tests you must run the tests with environment variables allowing access to this database.
    Eg, if you have defined a user tuttle with password tuttle, you can run the tests like this on Linux :
        export PGUSER=tuttle
        export PGPASSWORD=tuttle
        nosetests
    """

    __test_db_host = "localhost"
    __test_db_name = "tuttle_test_db"
    __test_db_port = 5432

    def setUp(self):
        try:
            conn_string = "host=\'{}\' dbname='{}' port={}".format(self.__test_db_host, self.__test_db_name,
                                                                   self.__test_db_port)
            conn = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            raise SkipTest("No postgreSQL database configured to mock the ODBC tests")
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS test_table CASCADE")
        cur.execute("CREATE TABLE test_table (col1 INT)")
        cur.execute("INSERT INTO test_table (col1) VALUES (12)")
        conn.commit()

    def test_odbc_processor_should_be_availlable(self):
        """A project with a PostgreSQL processor should be Ok"""
        project = "odbc://tuttle_test_db/another_test_table <- odbc://tuttle_test_db/test_table ! odbc"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "odbc"

    @isolate
    def test_odbc_processor(self):
        """A project with a PostgreSQL processor should run the sql statements"""
        project = """odbc://tuttle_test_db/new_table <- odbc://tuttle_test_db/test_table ! odbc
        CREATE TABLE new_table AS SELECT * FROM test_table;
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("CREATE TABLE new_table AS SELECT * FROM test_table") > -1, \
            "ODBCProcessor should log the SQL statements"

    def test_static_check_should_fail_if_across_several_odbc_databases(self):
        """The ODBC processor can't decide which database to connect to"""
        project = "odbc://tuttle_test_db/new_table <- odbc://another_db/test_table ! odbc"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "odbc"
        try:
            process.static_check()
            assert False, "Static check should not have allowed connection"
        except TuttleError:
            assert True

    @isolate
    def test_odbc_processor_with_several_instuctions(self):
        """ An ODBC process can have several SQL instructions and create several tables"""
        project = """odbc://tuttle_test_db/new_table, odbc://tuttle_test_db/another_table <- odbc://tuttle_test_db/test_table ! odbc
        CREATE TABLE new_table AS SELECT * FROM test_table;
        CREATE TABLE another_table (id int, col1 varchar);
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

    @isolate
    def test_sql_error_in_odbc_processor(self):
        """ If an error occurs, tuttle should fail and output logs should trace the error"""
        project = """odbc://tuttle_test_db/new_table <- odbc://tuttle_test_db/test_table ! odbc
        CREATE TABLE new_table AS SELECT * FROM test_table;

        NOT an SQL statement;
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 2, output
        error_log = open(join('.tuttle', 'processes', 'logs', 'tuttlefile_1_err.txt')).read()
        assert error_log.find('"NOT"') >= 0, error_log

    @isolate
    def test_comments_in_process(self):
        """ Comments should be ignored and not considered as errors"""
        project = """odbc://tuttle_test_db/new_table <- odbc://tuttle_test_db/test_table ! odbc
        CREATE TABLE new_table AS SELECT * FROM test_table;
        -- This is a comment
        /* last comment style*/
        """
        rcode, output = run_tuttle_file(project)
        error_log = open(join('.tuttle', 'processes', 'logs', 'tuttlefile_1_err.txt')).read()
        assert rcode == 0, error_log
        assert output.find("comment") >= 0

    def test_check_ok_with_no_outputs(self):
        """static check should work even if there are no outputs"""
        project = " <- odbc://tuttle_test_db/test_table ! odbc"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "odbc"
        process.static_check()

    def test_static_check_ok_with_no_inputs(self):
        """Static check should work even if there are no inputs"""
        project = "odbc://tuttle_test_db/test_table <- ! odbc"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "odbc"
        process.static_check()

    def test_static_check_should_fail_without_odbc_resources(self):
        """Static check should fail if no ODBC resources are specified either in inputs or outputs"""
        project = "<- ! odbc"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "odbc"
        try:
            process.static_check()
            assert False, "Static check should not have allowed ODBC proccessor without ODBC resource"
        except TuttleError as e:
            assert e.message.find("at least") >= 0, e.message
            assert True
