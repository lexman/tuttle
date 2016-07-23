# -*- coding: utf8 -*-
from itertools import chain

import sqlite3
from sqlite3 import OperationalError
from os import remove
from os.path import isfile
from re import compile
from tuttle.error import TuttleError
from tuttle.resources import MalformedUrl, ResourceMixIn
from hashlib import sha1


class SQLiteTuttleError(TuttleError):
    pass


class SQLiteProcessor:
    """ A processor for Windows command line
    """
    name = 'sqlite'

    def _get_sqlite_file(self, process):
        filename = None
        for resource in chain(process.iter_inputs(), process.iter_outputs()):
            if isinstance(resource, SQLiteResource):
                if filename is None:
                    filename = resource.db_file
                elif filename != resource.db_file:
                    raise SQLiteTuttleError(
                        "SQLite processor can't handle process over several SQLite databases. "
                        "Found files {} and {}.".format(filename, resource.db_file))
        return filename

    def static_check(self, process):
        # Will raise if file is ambiguous
        for resource in chain(process.iter_inputs(), process.iter_outputs()):
            if not isinstance(resource, SQLiteResource):
                raise SQLiteTuttleError("Sorry, SQLite Processor can only handle SQLite resources "
                                        "as inputs or outputs. Found : '{}'".format(resource.url))
        sqlite_file = self._get_sqlite_file(process)
        if sqlite_file is None:
            raise SQLiteTuttleError(
                "SQLite processor needs at least a SQLite resource as input or output... Don't know which database to connect to !")

    def run(self, process, reserved_path, log_stdout, log_stderr):
        sqlite_file = self._get_sqlite_file(process)
        db = sqlite3.connect(sqlite_file)
        with open(log_stdout, "w") as lout, open(log_stderr, "w") as lerr:
            try:
                lout.write(process._code)
                lout.write("\n")
                db.executescript(process._code)
            except OperationalError as e:
                lerr.write(e.message)
                lerr.write("\n")
                msg = "Error while running SQLite process {} : '{}'".format(process.id, e.message)
                raise SQLiteTuttleError(msg)
            finally:
                db.close()


class SQLiteResource(ResourceMixIn, object):
    """A resource for a table in a SQLite database"""
    """eg : sqlite://relative/path/to/sqlite_file/mytable"""
    scheme = 'sqlite'

    ereg = compile("^sqlite://(.*)/([^/]*)$")

    def __init__(self, url):
        super(SQLiteResource, self).__init__(url)
        m = self.ereg.match(url)
        if m is None:
            raise MalformedUrl("Malformed Sqlite url : '{}'".format(url))
        self.db_file = m.group(1)
        self.objectname = m.group(2)

    def sqlite_object_type(self, db, objectname):
        """Generate a hash for the contents of a file."""
        cur = db.cursor()
        cur.execute("SELECT type FROM sqlite_master WHERE name=?", (objectname, ))
        row = cur.fetchone()
        return row[0]

    def exists(self):
        if not isfile(self.db_file):
            return False
        db = sqlite3.connect(self.db_file)
        db.row_factory = sqlite3.Row
        try:
            cur = db.cursor()
            cur.execute("SELECT * FROM sqlite_master WHERE name=?", (self.objectname, ))
            row = cur.fetchone()
            if not row:
                return False
        finally:
            db.close()
        return True

    def table_signature(self, db, tablename):
        """Generate a hash for the contents of a file."""
        checksum = sha1()
        cur = db.cursor()
        cur.execute("SELECT sql FROM sqlite_master WHERE name=?", (self.objectname, ))
        row = cur.fetchone()
        checksum.update(row[0])
        db.execute("SELECT * FROM `{}`".format(tablename))
        for row in cur:
            for field in row:
                checksum.update(field)
        return checksum.hexdigest()

    def db_declaration(self, db, objectname):
        """Generate a hash for the contents of a file."""
        cur = db.cursor()
        cur.execute("SELECT sql FROM sqlite_master WHERE name=?", (objectname, ))
        row = cur.fetchone()
        return row[0]

    def signature(self):
        db = sqlite3.connect(self.db_file)
        db.text_factory = str
        try:
            obj_type = self.sqlite_object_type(db, self.objectname)
            if obj_type == "table":
                result = self.table_signature(db, self.objectname)
            elif obj_type == "index" or obj_type == "view" or obj_type == "trigger":
                result = self.db_declaration(db, self.objectname)
        finally:
            db.close()
        return result

    def remove_file_if_empty(self, db):
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM sqlite_master AS nb")
        raw = cur.fetchone()
        if raw[0] == 0:
            db.close()
            remove(self.db_file)

    def remove_table(self, db, tablename):
        db.execute("DROP TABLE `{}`".format(tablename))

    def remove_index(self, db, tablename):
        db.execute("DROP INDEX `{}`".format(tablename))

    def remove_view(self, db, tablename):
        db.execute("DROP VIEW `{}`".format(tablename))

    def remove_trigger(self, db, tablename):
        db.execute("DROP TRIGGER `{}`".format(tablename))

    def remove(self):
        db = sqlite3.connect(self.db_file)
        try:
            obj_type = self.sqlite_object_type(db, self.objectname)
            if obj_type == "table":
                self.remove_table(db, self.objectname)
            elif obj_type == "index":
                self.remove_index(db, self.objectname)
            elif obj_type == "view":
                self.remove_view(db, self.objectname)
            elif obj_type == "trigger":
                self.remove_trigger(db, self.objectname)
            self.remove_file_if_empty(db)
        finally:
            db.close()
