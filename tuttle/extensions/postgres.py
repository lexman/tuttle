# -*- coding: utf8 -*-

from re import compile
from tuttle.resources import MalformedUrl, ResourceMixIn
import psycopg2

class PostgreSQLResource(ResourceMixIn, object):
    """A resource for an object in a PostgreSQL database. Objects can be tables, view..."""
    """eg : pg://localhost:5432/tuttle_test_database/test_schema/test_table"""
    scheme = 'postgres'

    __ereg = compile("^pg://([^/^:]*)(:[0-9]*)?/([^/]*)/([^/]*/)?([^/]*)$")

    def __init__(self, url):
        super(PostgreSQLResource, self).__init__(url)
        m = self.__ereg.match(url)
        if m is None:
            raise MalformedUrl("Malformed PostgreSQL url : '{}'".format(url))
        self._server = m.group(1)
        captured_port = m.group(2)
        if captured_port:
            self._port = captured_port[1:]
        else:
            self._port = None
        self._database = m.group(3)
        captured_schema = m.group(4)
        if captured_schema:
            self._schema = m.group(4)[:-1]
        else:
            self._schema = "public"
        self._objectname = m.group(5)

    def exists(self):
        try:
            conn_string = "host=\'{}\' dbname='{}' port={} user=tuttle password=tuttle".format(self._server, self._database,
                                                                   self._port)
            db = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            return False
        try:
            cur = db.cursor()
            query = "SELECT * FROM pg_catalog.pg_tables WHERE tablename=%s AND schemaname=%s"
            cur.execute(query, (self._objectname, self._schema))
            row = cur.fetchone()
            if not row:
                return False
        except psycopg2.OperationalError:
            return False
        finally:
            db.close()
        return True

    def remove(self):
        try:
            conn_string = "host=\'{}\' dbname='{}' port={} user=tuttle password=tuttle".format(self._server, self._database,
                                                                   self._port)
            db = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            return False
        try:
            cur = db.cursor()
            cur.execute('DROP TABLE "{}"."{}"'.format(self._schema, self._objectname))
            db.commit()
        finally:
            db.close()
