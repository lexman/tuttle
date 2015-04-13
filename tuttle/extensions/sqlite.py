# -*- coding: utf8 -*-

import sqlite3
from sqlite3 import OperationalError
from os.path import isfile
from re import compile
from tuttle.resources import MalformedUrl



class SQLiteResource:
    """A resource for a table in a SQLite database"""
    """eg : sqlite://relative/path/to/sqlite_file/tables/mytable"""
    scheme = 'sqlite'

    ereg = compile("^sqlite://(.*)/tables/([^/]*)$")

    def __init__(self, url):
        self.url = url
        self.creator_process = None
        m = self.ereg.match(url)
        if m is None:
            raise MalformedUrl("Malformed Sqlite url : '{}'".format(url))
        self.db_file = m.group(1)
        self.table = m.group(2)

    def set_creator_process(self, process):
        self.creator_process = process

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

    def remove(self):
        db = sqlite3.connect(self.db_file)
        db.row_factory = sqlite3.Row
        try:
            cur = db.cursor()
            cur.execute("DROP TABLE {}".format(self.table))
        finally:
            db.close()


