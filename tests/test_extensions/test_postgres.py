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
            conn_string = "host=\'{}\' dbname='{}' port={}".format(self.__test_db_host, self.__test_db_name,
                                                                   self.__test_db_port)
            conn = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            raise SkipTest("No postgreSQL database configured to run the tests")

    def test_parse_standard_url(self):
        """A standard pg url should provide a valid resource"""
        url = "pg://localhost:5432/tuttle_test_db/test_schema/test_table"
        res = PostgreSQLResource(url)
        assert res._server == "localhost", res._server
        assert res._port == "5432", res._port
        assert res._database == "tuttle_test_database", res._database
        assert res._schema == "test_schema", res._schema
        assert res._objectname == "test_table", res._objectname

    def test_port_is_optional_in_url(self):
        """Port can be omitted in pg url"""
        url = "pg://localhost/tuttle_test_database/test_schema/test_table"
        res = PostgreSQLResource(url)
        assert res._server == "localhost", res._server
        assert res._port is None , res._port
        assert res._database == "tuttle_test_database", res._database
        assert res._schema == "test_schema", res._schema
        assert res._objectname == "test_table", res._objectname

    def test_schema_is_optional_in_pg_url(self):
        """Schema can be omited in pg url"""
        url = "pg://localhost:5432/tuttle_test_database/test_table"
        res = PostgreSQLResource(url)
        assert res._server == "localhost", res._server
        assert res._port == "5432", res._port
        assert res._database == "tuttle_test_database", res._database
        assert res._schema is None, res._schema
        assert res._objectname == "test_table", res._objectname

    def test_pg_table_exists(self):
        """exists() should return True when the table exists"""
        url = "pg://localhost:5432/tuttle_test_database/test_schema/test_table"
        res = PostgreSQLResource(url)
        assert res.exists()
