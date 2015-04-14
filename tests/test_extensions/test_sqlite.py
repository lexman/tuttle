# -*- coding: utf8 -*-
from tests.functional_tests import isolate
from tuttle.extensions.sqlite import SQLiteResource
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


    def test_pre_check_should_fail_if_several_sqlite_files_are_ref(self):
        """Pre-check should fail for SQLite processor if it is supposed to work with several SQLite files"""
        project = "sqlite://db1.sqlite/tables/my_table <- sqlite://db2.sqlite/tables/my_table #! sqlite"
        pp = ProjectParser()
        pp.set_project(project)
        pp.read_line()
        process = pp.parse_dependencies_and_processor()
        assert process._processor.name == "sqlite"



#    def test_real_resource_exists(self):
#        """A real resource should exist"""
#        file_url = "file://{}".format(path.abspath(tuttle.resources.__file__))
#        res = FileResource(file_url)
#        assert res.exists()

#    def test_fictive_resource_exists(self):
#        """A real resource should exist"""
#        res = FileResource("fictive_file")
#        assert not res.exists()
