# -*- coding: utf8 -*-
from tests.functional_tests import isolate
from tuttle.extensions.sqlite import SQLiteResource


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
        assert res.exists() == True


#    def test_real_resource_exists(self):
#        """A real resource should exist"""
#        file_url = "file://{}".format(path.abspath(tuttle.resources.__file__))
#        res = FileResource(file_url)
#        assert res.exists()

#    def test_fictive_resource_exists(self):
#        """A real resource should exist"""
#        res = FileResource("fictive_file")
#        assert not res.exists()
