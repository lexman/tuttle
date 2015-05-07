# -*- coding: utf8 -*-
from itertools import chain

import sqlite3
from sqlite3 import OperationalError
from os import remove
from os.path import isfile
from re import compile
from tuttle.error import TuttleError
from tuttle.resources import MalformedUrl, ResourceMixIn


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

    def pre_check(self, process):
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
    """eg : sqlite://relative/path/to/sqlite_file/tables/mytable"""
    scheme = 'sqlite'

    ereg = compile("^sqlite://(.*)/tables/([^/]*)$")

    def __init__(self, url):
        super(SQLiteResource, self).__init__(url)
        m = self.ereg.match(url)
        if m is None:
            raise MalformedUrl("Malformed Sqlite url : '{}'".format(url))
        self.db_file = m.group(1)
        self.table = m.group(2)

    def exists(self):
        if not isfile(self.db_file):
            return False
        db = sqlite3.connect(self.db_file)
        db.row_factory = sqlite3.Row
        try:
            cur = db.cursor()
            cur.execute("SELECT * FROM {} LIMIT 0".format(self.table))
        except OperationalError:
            return False
        finally:
            db.close()
        return True

    # TODO : should we make a checksum of all the  data ?
    # or should we speedup the process by using the aproximate number of rows in sqlite_stat1 ?
    def signature(self):
        db = sqlite3.connect(self.db_file)
        try:
            cur = db.cursor()
            cur.execute("SELECT COUNT(*) AS nb FROM `{}`".format(self.table))
            row = cur.fetchone()
            nb = row[0]
            cur.execute("SELECT * FROM sqlite_master WHERE name=?", (self.table, ))
            sum_up = cur.fetchone()
            result = "|".join((sum_up[0], sum_up[1], sum_up[2], str(sum_up[3]), sum_up[4], str(nb), ))
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

    def remove(self):
        db = sqlite3.connect(self.db_file)
        try:
            db.execute("DROP TABLE `{}`".format(self.table))
            self.remove_file_if_empty(db)
        finally:
            db.close()
