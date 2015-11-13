# -*- coding: utf8 -*-
from tests.functional_tests import run_tuttle_file, isolate
from tuttle.extensions.postgres import PostgreSQLResource
from nose.plugins.skip import SkipTest
import psycopg2


class TestPostgresResource():
    """
    Test tuttle with Postgresql resources
    To ensure tests will be run, you must provide access to a local postgresql database called tuttle_test_db,
    then you must run the tests with environment variables allowing access to this database.
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
            raise SkipTest("No postgreSQL database configured to run the tests")
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS test_table CASCADE")
        cur.execute("CREATE TABLE test_table (col1 INT)")
        cur.execute("DROP VIEW IF EXISTS test_view")
        cur.execute("CREATE VIEW test_view AS SELECT * FROM test_table")
        cur.execute("DROP SCHEMA IF EXISTS test_schema CASCADE")
        cur.execute("CREATE SCHEMA test_schema")
        cur.execute("DROP TABLE IF EXISTS test_schema.test_table_in_schema")
        cur.execute("CREATE TABLE test_schema.test_table_in_schema (col1 INT)")
        cur.execute("INSERT INTO test_table (col1) VALUES (12)")
        cur.execute("""CREATE OR REPLACE FUNCTION test_function() RETURNS integer AS
$BODY$
BEGIN
    RETURN "42";
END;
$BODY$
  LANGUAGE plpgsql
""")
        cur.execute("""CREATE OR REPLACE FUNCTION test_function_args(integer, real) RETURNS integer AS
$BODY$
BEGIN
    RETURN "69";
END;
$BODY$
  LANGUAGE plpgsql
""")
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

    def test_table_signature(self):
        """signature() should return a hash of the structure and the data for a table"""
        url = "pg://localhost:5432/tuttle_test_db/test_table"
        res = PostgreSQLResource(url)
        sig = res.signature()
        expected = "a545767cf5742cb647ac7b507ac77960d737474a"
        assert sig == expected, sig

    def test_view_exists(self):
        """exists() should return True because the view exists"""
        url = "pg://localhost:5432/tuttle_test_db/test_view"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)

    def test_remove_view(self):
        """after remove, a view should no longer exist"""
        url = "pg://localhost:5432/tuttle_test_db/test_view"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)
        res.remove()
        assert not res.exists(), "{} should not exist any more !".format(url)

    def clean_view_sig(self, sig):
        """ Removes extra spaces and new lines from an SQL query for assert comparison
        """
        res = sig.strip()
        res = res.replace("\n", "")
        res = res.replace("\t", " ")
        while res.find("  ") >= 0:
            res = res.replace("  ", " ")
        return res

    def test_view_signature(self):
        """the declaration of a view should be its signature"""
        url = "pg://localhost:5432/tuttle_test_db/test_view"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)
        expected = "SELECT test_table.col1 FROM test_table;"
        sig = res.signature()
        assert self.clean_view_sig(sig) == expected, sig

    @isolate
    def test_pg_resources_are_available_in_tuttle(self):
        """A project with a postgres resource should be valid"""
        project = """pg://localhost:5432/tuttle_test_db/test_table_project <- ! python
            import psycopg2
            conn_string = "host=localhost dbname=tuttle_test_db"
            db = psycopg2.connect(conn_string)
            cur=db.cursor()
            cur.execute("CREATE TABLE test_table_project (col INT)")
            db.commit()
        """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("Done") >= 0, output

    def test_function_exists(self):
        """exists() should return True because the function exists"""
        url = "pg://localhost:5432/tuttle_test_db/test_function"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)

    def test_remove_function(self):
        """after remove, a function should no longer exist"""
        url = "pg://localhost:5432/tuttle_test_db/test_function"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)
        res.remove()
        assert not res.exists(), "{} should not exist anymore".format(url)

    def test_remove_function_with_args(self):
        """after remove, a function should no longer exist whatever its arguments"""
        url = "pg://localhost:5432/tuttle_test_db/test_function_args"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)
        res.remove()
        assert not res.exists(), "{} should not exist anymore".format(url)

    def test_function_signature(self):
        """the signature of a function should be a hash of its source code"""
        url = "pg://localhost:5432/tuttle_test_db/test_function_args"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)
        assert res.signature() == "b92433deca9384c90d6313f496ea4b67d5531983", res.signature()

    def test_schema_exists(self):
        """exists() should return True because the schema exists"""
        url = "pg://localhost:5432/tuttle_test_db/test_schema/"
        res = PostgreSQLResource(url)
        msg = " server : {}\n port : {}\ndb : {} \nschema : {}\n object {}".format(res._server, res._port, res._database, res._schema, res._objectname)
        assert res.exists(), msg
        assert res.exists(), "{} should exist".format(url)

    def test_remove_schema(self):
        """after remove, a schema should no longer exist"""
        url = "pg://localhost:5432/tuttle_test_db/test_schema/"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)
        res.remove()
        assert not res.exists(), "{} should not exist anymore".format(url)

    def test_schema_signature(self):
        """the signature of the schema should be its owner"""
        url = "pg://localhost:5432/tuttle_test_db/test_schema/"
        res = PostgreSQLResource(url)
        assert res.exists(), "{} should exist".format(url)
        assert res.signature() == "owner : tuttle", res.signature()

    def test_dont_mix_schema_and_object_signature(self):
        """If we omit the / at the end of the resource, it should not be interpreted as a schema"""
        url = "pg://localhost:5432/tuttle_test_db/test_schema"
        res = PostgreSQLResource(url)
        assert not res.exists(), "{} should not exist because no table, view nor any object with that name " \
                                 "exists".format(url)
