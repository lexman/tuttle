# -*- coding: utf8 -*-

from re import compile
from tuttle.resources import MalformedUrl, ResourceMixIn


class PostgreSQLResource(ResourceMixIn, object):
    """A resource for an object in a PostgreSQL database. Objects can be tables, view..."""
    """eg : pg://localhost:5432/tuttle_test_database/test_schema/test_table"""
    scheme = 'postgres'

    ereg = compile("^pg://([^/]*)(:[0-9]*)?/([^/]*/)?([^/]*)$")
    __ereg = compile("^pg://([^/^:]*)(:[0-9]*)?/([^/]*)/([^/]*/)?([^/]*)$")

    def __init__(self, url):
        super(PostgreSQLResource, self).__init__(url)
        m = self.__ereg.match(url)
        if m is None:
            raise MalformedUrl("Malformed PostgreSQL url : '{}'".format(url))
        self._server = m.group(1)
        self._port = m.group(2)[1:]
        self._database = m.group(3)
        self._schema = m.group(4)[:-1]
        self._objectname = m.group(5)

