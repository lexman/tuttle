# -*- coding: utf8 -*-

from re import compile
from tuttle.resources import MalformedUrl, ResourceMixIn
from hashlib import sha1
import psycopg2

class PostgreSQLResource(ResourceMixIn, object):
    """A resource for an object in a PostgreSQL database. Objects can be tables, view..."""
    """eg : pg://localhost:5432/tuttle_test_database/test_schema/test_table"""
    scheme = 'pg'

    __ereg = compile("^pg://([^/^:]*)(:[0-9]*)?/([^/]*)/([^/]*/)?([^/]*)$")

    TYPE_TABLE = 'r'
    TYPE_VIEW = 'v'
    TYPE_FUNCTION = 'f'

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

    def pg_object_type(self, db, schema, objectname):
        """Returns the type of object in the database, as a constant :
         * TYPE_VIEW for tables
         * TYPE_VIEW for views
         * TYPE_FUNCTION for functions
        """
        cur = db.cursor()
        query = """SELECT c.relname, c.relkind, n.nspname AS schema
                     FROM pg_class c
                       LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE relname=%s AND n.nspname=%s
        """
        cur.execute(query, (objectname, schema, ))
        row = cur.fetchone()
        if row:
            return row[1]
        query = """SELECT p.proname, n.nspname AS schema
                     FROM pg_proc p
                       LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
                    WHERE proname=%s AND n.nspname=%s
        """
        cur.execute(query, (objectname, schema, ))
        row = cur.fetchone()
        if row:
            return 'f'

    def exists(self):
        try:
            conn_string = "host=\'{}\' dbname='{}' port={} ".format(self._server, self._database,
                                                                   self._port)
            db = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            return False
        try:
            result = self.pg_object_type(db, self._schema, self._objectname) is not None
        except psycopg2.OperationalError:
            return False
        finally:
            db.close()
        return result

    def remove_table(self, cur, schema, name):
        cur.execute('DROP TABLE "{}"."{}" CASCADE'.format(schema, name))

    def remove_view(self, cur, schema, name):
        cur.execute('DROP VIEW "{}"."{}" CASCADE'.format(schema, name))

    def pg_type_names(self, cur, oids):
        """
        :param cur: a cursor on a postgresql database
        :param oids: a string with postgresql oid separated by spaces
        :return: an array of the fully qualified names of the postgres types
        """
        if len(oids) == 0:
            return []
        oids_seq = oids.replace(' ', ',')
        query = """SELECT t.oid, t.typname, n.nspname AS schema
                     FROM pg_type t
                       LEFT JOIN pg_namespace n ON n.oid = t.typnamespace
                    WHERE t.oid in ({})
        """.format(oids_seq)
        cur.execute(query, (self._objectname, self._schema, ))
        match = {str(row[0]): '"{}"."{}"'.format(row[2], row[1]) for row in cur}
        res = [match[oid] for oid in oids.split(' ')]
        return res

    def function_arguments(self, cur, schema, name):
        """ Returns the list of types of arguments of a postgresql function
        :param cur: a cursor open on a postgresql database
        :param schema: schema name of the function
        :param name: function name
        :return: string : a coma separated list of arguments
        """
        query = """SELECT p.proname, n.nspname, p.proargtypes AS schema
                     FROM pg_proc p
                       LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
                    WHERE proname=%s AND n.nspname=%s
        """
        cur.execute(query, (name, schema, ))
        row = cur.fetchone()
        args_oids = row[2]
        arg_types = ", ".join(self.pg_type_names(cur, args_oids))
        return arg_types

    def remove_function(self, cur, schema, name):
        """ Removes a function from the database.
        The database should have only one function with this name (ie no overload with several signatures
        with different arguments) because if will remove one and only one of them
        :param cur: a postgresql cursor
        """
        args = self.function_arguments(cur, schema, name)
        query_drop = 'DROP FUNCTION "{}"."{}"({}) CASCADE'.format(schema, name, args)
        cur.execute(query_drop)

    def remove(self):
        try:
            conn_string = "host=\'{}\' dbname='{}' port={}".format(self._server, self._database,
                                                                   self._port)
            db = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            return False
        try:
            cur = db.cursor()
            obj_type = self.pg_object_type(db, self._schema, self._objectname)
            if obj_type == self.TYPE_TABLE:
                self.remove_table(cur, self._schema, self._objectname)
            elif obj_type == self.TYPE_VIEW:
                self.remove_view(cur, self._schema, self._objectname)
            elif obj_type == self.TYPE_FUNCTION:
                self.remove_function(cur, self._schema, self._objectname)
            db.commit()
        finally:
            db.close()

    def table_signature(self, db, schema, tablename):
        """Generate a hash for the contents of a table."""
        checksum = sha1()
        cur = db.cursor()
        query = """SELECT *
                    FROM information_schema.columns
                    WHERE table_name=%s AND table_schema=%s
                    ORDER BY column_name;
                """
        cur.execute(query, (tablename, schema))
        for row in cur:
            for field in row:
                checksum.update(str(field))
        cur.execute('SELECT * FROM "{}"'.format(tablename))
        for row in cur:
            for field in row:
                checksum.update(str(field))
        return checksum.hexdigest()

    def view_signature(self, db, schema, tablename):
        """Returns the definition of the view"""
        cur = db.cursor()
        query = """SELECT view_definition
                    FROM information_schema.views
                    WHERE table_name=%s AND table_schema=%s
                """
        cur.execute(query, (tablename, schema))
        row = cur.fetchone()
        return row[0]

    def function_signature(self, db, schema, name):
        """Returns a hash of the function source."""
        checksum = sha1()
        cur = db.cursor()
        query = """SELECT p.proname, n.nspname AS schema, p.prosrc
                     FROM pg_proc p
                       LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
                    WHERE proname=%s AND n.nspname=%s
        """
        cur.execute(query, (name, schema, ))
        _, _, function_src = cur.fetchone()
        checksum.update(str(function_src))
        return checksum.hexdigest()


    def signature(self):
        try:
            conn_string = "host=\'{}\' dbname='{}' port={}".format(self._server, self._database,
                                                                   self._port)
            db = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            return False
        result = False
        try:
            object_type = self.pg_object_type(db, self._schema, self._objectname)
            if object_type == self.TYPE_TABLE:
                result = self.table_signature(db, self._schema, self._objectname)
            elif object_type == self.TYPE_VIEW:
                result = self.view_signature(db, self._schema, self._objectname)
            elif object_type == self.TYPE_FUNCTION:
                result = self.function_signature(db, self._schema, self._objectname)
        finally:
            db.close()
        return result