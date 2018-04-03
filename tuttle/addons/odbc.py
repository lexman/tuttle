# -*- coding: utf8 -*-

from itertools import chain
from re import compile
from urlparse import parse_qs

from tuttle.error import TuttleError
from tuttle.resource import MalformedUrl, ResourceMixIn
from hashlib import sha1
import pyodbc


class ODBCResource(ResourceMixIn, object):
    """A resource for a table or e view in an ODBC database."""
    """eg : odbc://datasource_name/test_table"""
    scheme = 'odbc'

    __ereg = compile("^odbc://([^/^:]*)/([^/^?]*)(\?.*)?$")

    def query2filters(self, query, url):
        try:
            filters = parse_qs(query, strict_parsing=True)
            for col, values in filters.items():
                if len(values) > 1:
                    raise MalformedUrl("Malformed filter '{}' in ODBC url '{}'. "
                                       "Too many values : '{}'".format(col, url, ','.join(values)))
                else:
                    filters[col] = values[0]
        except ValueError:
            raise MalformedUrl("Malformed filters '{}' in ODBC url : '{}'".format(query, url))
        return filters

    def __init__(self, url):
        super(ODBCResource, self).__init__(url)
        m = self.__ereg.match(url)
        if m is None:
            raise MalformedUrl("Malformed ODBC url : '{}'".format(url))
        self._dsn = m.group(1)
        self._relation = m.group(2)
        qs = m.group(3)
        if qs:
            self._filters = self.query2filters(qs[1:], url)
        else:
            self._filters = None

    def where_filter(self, filters):
        if not filters:
            return "", ()
        keys = []
        values = []
        for key, value in filters.items():
            keys.append(key)
            values.append(value)
        where_keys = ' AND '.join(["{} = ?".format(key) for key in keys])
        return "WHERE {}".format(where_keys), values

    def exists_partition(self, conn, relation, filters):
        cur = conn.cursor()
        where, values = self.where_filter(filters)
        query = "SELECT 1 FROM {} {} LIMIT 1".format(relation, where)
        try:
            cur.execute(query, values)
            row = cur.fetchone()
            return row is not None
        except pyodbc.ProgrammingError:
            filter_st = ' AND '.join(("{}={}".format(key, value) for key, value in filters.items()))
            raise TuttleError("Error checking existance of partition {}. "
                              "Does table {} does exists ?".format(filter_st, relation))
        finally:
            conn.close()

    def exists_table(self, conn, relation):
        cur = conn.cursor()
        query = "SELECT * FROM {} LIMIT 0".format(relation)
        try:
            cur.execute(query)
            conn.close()
        except pyodbc.ProgrammingError:
            return False
        return True

    def exists(self):
        conn_string = "dsn={}".format(self._dsn)
        try:
            conn = pyodbc.connect(conn_string)
        except pyodbc.InterfaceError:
            raise TuttleError("Can't connect to DSN : \"{}\" to check existence of resource {}. "
                              "Have you declared the Data Source Name ?".format(conn_string, self.url))
        if self._filters:
            return self.exists_partition(conn, self._relation, self._filters)
        else:
            return self.exists_table(conn, self._relation)

    def remove_table(self, cursor, relation):
        query = "DROP TABLE {}".format(relation)
        cursor.execute(query)

    def remove_partition(self, cursor, relation, filters):
        where, values = self.where_filter(filters)
        query = "DELETE FROM {} {}".format(relation, where)
        cursor.execute(query, values)

    def remove(self):
        conn_string = "dsn={}".format(self._dsn)
        try:
            conn = pyodbc.connect(conn_string)
        except pyodbc.InterfaceError:
            return False
        try:
            cur = conn.cursor()
            if self._filters:
                self.remove_partition(cur, self._relation, self._filters)
            else:
                self.remove_table(cur, self._relation)
            cur.commit()
        finally:
            conn.close()

    def relation_hash(self, db, relation, filters):
        """Generate a hash for the contents of a table."""
        checksum = sha1()
        cur = db.cursor()
        where, values = self.where_filter(filters)
        cur.execute('SELECT * FROM "{}" {}'.format(relation, where), values)
        for row in cur:
            for field in row:
                checksum.update(str(field))
        return checksum.hexdigest()

    def signature(self):
        conn_string = "dsn={}".format(self._dsn)
        try:
            conn = pyodbc.connect(conn_string)
        except pyodbc.InterfaceError:
            return False
        try:
            return self.relation_hash(conn, self._relation, self._filters)
        finally:
            conn.close()

    @staticmethod
    def check_consistency(workflow):
        odbc_not_primary = (res for res in workflow.iter_resources()
                            if isinstance(res, ODBCResource) and not res.is_primary())
        references = {}
        for res in odbc_not_primary:
            if res._relation not in references:
                references[res._relation] = res
            else:
                if references[res._relation]._filters != res._filters:
                    # TODO
                    INCOHERENT_PARTITIONS = "ODBC table {} have incoherent partitions {} and {}. The filters must be " \
                                            "the same to avoid overlapping of filters when creating resources. " \
                                            "See http://github.com/lexman/tuttle/docs/TODO"
                    msg = INCOHERENT_PARTITIONS.format(res._relation, references[res._relation].url, res.url)
                    raise TuttleError(msg)


class ODBCProcessor:
    """ A processor that runs sql directly in an odbc database
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
                        "Found connections string '{}' and '{}'.".format(conn_string, resource_conn_string))
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
                    query_err_mess = e.args[1]
                    lerr.write(query_err_mess)
                    lerr.write("\n")
                    msg = "Error while running ODBC process {} : '{}'".format(process.id, query_err_mess)
                    raise TuttleError(msg)
        except pyodbc.InterfaceError:
            return False
        finally:
            db.close()

