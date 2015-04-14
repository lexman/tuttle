# -*- coding: utf8 -*-
from tests.functional_tests import isolate
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

#    def test_real_resource_exists(self):
#        """A real resource should exist"""
#        file_url = "file://{}".format(path.abspath(tuttle.resources.__file__))
#        res = FileResource(file_url)
#        assert res.exists()

#    def test_fictive_resource_exists(self):
#        """A real resource should exist"""
#        res = FileResource("fictive_file")
#        assert not res.exists()
