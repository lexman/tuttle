# -*- coding: utf8 -*-
from tuttle.extensions.postgres import PostgreSQLResource
from nose.plugins.skip import SkipTest
import psycopg2


class TestPostgresResource():

    __test_db_host = "localhost"
    __test_db_name = "tuttle_test_db"
    __test_db_port = 5432

    def setUp(self):
        try:
            conn_string = "host=\'{}\' dbname='{}' port={} user=tuttle password=tuttle".format(self.__test_db_host, self.__test_db_name,
                                                                   self.__test_db_port)
            conn = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            raise SkipTest("No postgreSQL database configured to run the tests")
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS test_table")
        cur.execute("CREATE TABLE test_table (col1 INT)")
        cur.execute("DROP SCHEMA IF EXISTS test_schema CASCADE")
        cur.execute("CREATE SCHEMA test_schema")
        cur.execute("DROP TABLE IF EXISTS test_schema.test_table_in_schema")
        cur.execute("CREATE TABLE test_schema.test_table_in_schema (col1 INT)")
        conn.commit()

    def test_parse_standard_url(self):
        """A standard pg url should provide a valid resource"""
        url = "pg://localhost:5432/tuttle_test_db/test_schema/test_table"
        res = PostgreSQLResource(url)
        assert res._server == "localhost", res._server
        assert res._port == "5432", res._port
        assert res._database == "tuttle_test_db", res._database
        assert res._schema == "test_schema", res._schema
        assert res._objectname == "test_table", res._objectname

    def test_port_is_optional_in_url(self):
        """Port can be omitted in pg url"""
        url = "pg://localhost/tuttle_test_db/test_schema/test_table"
        res = PostgreSQLResource(url)
        assert res._server == "localhost", res._server
        assert res._port is None , res._port
        assert res._database == "tuttle_test_db", res._database
        assert res._schema == "test_schema", res._schema
        assert res._objectname == "test_table", res._objectname

    def test_schema_is_optional_in_pg_url(self):
        """Schema can be omited in pg url"""
        url = "pg://localhost:5432/tuttle_test_db/test_table"
        res = PostgreSQLResource(url)
        assert res._server == "localhost", res._server
        assert res._port == "5432", res._port
        assert res._database == "tuttle_test_db", res._database
        assert res._schema =="public", res._schema
        assert res._objectname == "test_table", res._objectname

    def test_pg_table_exists(self):
        """exists() should return True when the table exists"""
        url = "pg://localhost:5432/tuttle_test_db/test_table"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)

    def test_pg_table_not_exists(self):
        """the table should not exist"""
        url = "pg://localhost:5432/tuttle_test_db/no_table"
        res = PostgreSQLResource(url)
        assert not res.exists(), "{} should exist".format(url)

    def test_pg_table_with_schema_exists(self):
        """exists() the table should exist in the schema"""
        url = "pg://localhost:5432/tuttle_test_db/test_schema/test_table_in_schema"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)

    def test_pg_table_outside_schema_does_not_exist(self):
        """the table should exist if it isn't in the proper schema"""
        url = "pg://localhost:5432/tuttle_test_db/test_schema/test_table"
        res = PostgreSQLResource(url)
        assert not res.exists(), "{} should not exist".format(url)

    def test_remove_table(self):
        """remove() should remove a table"""
        url = "pg://localhost:5432/tuttle_test_db/test_table"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)
        res.remove()
        assert not res.exists(), "{} should not exist".format(url)
