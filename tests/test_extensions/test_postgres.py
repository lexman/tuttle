# -*- coding: utf8 -*-
from tuttle.extensions.postgres import PostgreSQLResource
from nose.plugins.skip import SkipTest


class TestPostgresResource():

    def setUp(self):
        #raise SkipTest()
        pass

#    def test_should_be_skipped(self):
#        raise Exception("Should not have been executed")

    def test_parse_url(self):
        """A standard pg url should work"""
        url = "pg://localhost:5432/tuttle_test_database/test_schema/test_table"
        res = PostgreSQLResource(url)
        assert res._server == "localhost", res._server
        assert res._port == "5432", res._port
        assert res._database == "tuttle_test_database", res._database
        assert res._schema == "test_schema", res._schema
        assert res._objectname == "test_table", res._objectname
