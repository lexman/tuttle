# -*- coding: utf8 -*-
from itertools import chain

from re import compile

from tuttle.addons.netutils import hostname_resolves
from tuttle.error import TuttleError
from tuttle.resource import MalformedUrl, ResourceMixIn
from hashlib import sha1
import pyodbc


class ODBCResource(ResourceMixIn, object):
    """A resource for a table or e view in an ODBC database."""
    """eg : odbc://datasource_name/test_table"""
    scheme = 'odbc'

    __ereg = compile("^odbc://([^/^:]*)/([^/]*)$")

    def __init__(self, url):
        super(ODBCResource, self).__init__(url)
        m = self.__ereg.match(url)
        if m is None:
            raise MalformedUrl("Malformed ODBC url : '{}'".format(url))
        self._dsn = m.group(1)
        self._relation = m.group(2)


    def exists(self):
        conn_string = "dsn={}".format(self._dsn)
        try:
            conn = pyodbc.connect(conn_string)
        except pyodbc.InterfaceError as e:
            raise TuttleError("Can't connect to DSN : \"{}\" to "
                              "check existence of resource {}. Have you declared the Data Source Name ?".format(conn_string, self.url))

        query = "SELECT * FROM {} LIMIT 0".format(self._relation)
        cur = conn.cursor()
        try:
            cur.execute(query)
            conn.close()
        except pyodbc.ProgrammingError as e:
            return False
        return True

    def remove(self):
        conn_string = "dsn={}".format(self._dsn)
        try:
            conn = pyodbc.connect(conn_string)
        except pyodbc.InterfaceError as e:
            return False
        try:
            cur = conn.cursor()
            query = "DROP TABLE {}".format(self._relation)
            cur.execute(query)
            cur.commit()
        finally:
            conn.close()

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

    def signature(self):
        conn_string = "dsn={}".format(self._dsn)
        try:
            conn = pyodbc.connect(conn_string)
        except pyodbc.InterfaceError as e:
            return False
        try:
            checksum = sha1()
            cur = conn.cursor()
            cur.execute('SELECT * FROM "{}"'.format(self._relation))
            for row in cur:
                for field in row:
                    checksum.update(str(field))
            return checksum.hexdigest()
        finally:
            conn.close()




class ODBCProcessor:
    """ A processor that runs sql directely in a postgres database
    """
    name = 'odbc'

    def _get_db_connection_string(self, process):
        conn_string = None
        for resource in chain(process.iter_inputs(), process.iter_outputs()):
            if isinstance(resource, ODBCResource):
                resource_conn_string = "dsn={}".format(resource._dsn)
                if conn_string is None:
                    conn_string = resource_conn_string
                elif conn_string != resource_conn_string:
                    raise TuttleError(
                        "ODBC processor can't connect to several ODBC databases at the same time. "
                        "Found connections string '{}' and '{}'.".format(conn_string , resource_conn_string))
        return conn_string

    def static_check(self, process):
        # Will raise if there is an ambiguity on the database
        for resource in chain(process.iter_inputs(), process.iter_outputs()):
            if not isinstance(resource, ODBCResource):
                raise TuttleError("Sorry, ODBC Processor can only handle ODBC resources "
                                  "as inputs or outputs. Found : '{}'".format(resource.url))
        connection_string = self._get_db_connection_string(process)
        if connection_string is None:
            raise TuttleError(
                "ODBC processor needs at least an odbc:// resource as input or output... Don't know which database DSN to connect to !")

    def run(self, process, reserved_path, log_stdout, log_stderr):
        connection_string = self._get_db_connection_string(process)
        try:
            db = pyodbc.connect(connection_string)
            with open(log_stdout, "w") as lout, \
                    open(log_stderr, "w") as lerr, \
                    db.cursor() as cursor:
                try:
                    lout.write(process._code)
                    cursor.execute(process._code)
                    db.commit()
                except Exception as e:
                    lerr.write(e.message)
                    lerr.write("\n")
                    msg = "Error while running ODBC process {} : '{}'".format(process.id, e.message)
                    raise TuttleError(msg)
        except pyodbc.InterfaceError as e:
            return False
        finally:
            db.close()

