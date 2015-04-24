# -*- coding: utf8 -*-
import csv
import sqlite3
from sqlite3 import OperationalError
from os import remove

from os.path import abspath, exists
from tuttle.error import TuttleError
from tuttle.extensions.sqlite import SQLiteResource
from tuttle.resources import ResourceMixIn


class CSVResource(ResourceMixIn, object):
    """A resource for a CSV file (with header) """
    """eg : csv://relative/path/to/myfile.csv"""
    scheme = 'csv'

    def __init__(self, url):
        super(CSVResource, self).__init__(url)
        self._path = self._get_path()

    def _get_path(self):
        return abspath(self.url[len("csv://"):])

    def exists(self):
        return exists(self._path)

    def remove(self):
        remove(self._path)


def strip_backstophes(st):
    return st.replace('`', '')


def escape_column_name(st):
    return '`{}`'.format(strip_backstophes(st))


def column_list(column_names):
    escaped_columns = map(escape_column_name, column_names)
    return ','.join(escaped_columns)


def create_table(db, table_name, column_names):
    columns = column_list(column_names)
    sql = "CREATE TABLE `{}` ({})".format(table_name, columns)
    print sql
    db.execute(sql)


def open_csv(csv_file):
    sample = csv_file.read(1024)
    csv_file.seek(0)
    dialect = csv.Sniffer().sniff(sample)
    return csv.reader(csv_file, dialect)


def fill_table(db, table_name, column_names, csv_reader):
    place_holders = ",".join(["?" for _ in column_names])
    columns = column_list(column_names)
    sql = "INSERT INTO `{}` ({}) VALUES ({})".format(table_name, columns, place_holders)
    db.executemany(sql, csv_reader)
    db.commit()


# TODO : handle utf8
def csv2sqlite(db, table_name, csv_file):
    csv_reader = open_csv(csv_file)
    column_names = csv_reader.next()
    create_table(db, table_name, column_names)
    fill_table(db, table_name, column_names, csv_reader)


class CSV2SQLiteProcessor:
    """ A processor for Windows command line
    """
    name = 'csv2sqlite'

    def pre_check(self, process):
        inputs = [res for res in process.iter_inputs()]
        outputs = [res for res in process.iter_outputs()]
        if len(inputs) != 1 \
           or len(outputs) != 1 \
           or inputs[0].scheme != 'csv' \
           or outputs[0].scheme != 'sqlite':
            raise TuttleError("CSV2SQLite processor {} don't know how to handle his inputs / outputs".format(process.id))

    def run(self, process, reserved_path, log_stdout, log_stderr):
        # TODO : log queries
        # pre_check ensured we know what are inputs and outputs
        input_res = process.iter_inputs().next()
        assert isinstance(input_res, CSVResource)
        csv_filename = input_res._path

        output_res = process.iter_outputs().next()
        assert isinstance(output_res, SQLiteResource)
        sqlite_filename = output_res.db_file
        table = output_res.table

        with open(log_stdout, "w") as lout, \
             open(log_stderr, "w") as lerr, \
             open(csv_filename, 'rb') as csv_file:
            try:
                db = sqlite3.connect(sqlite_filename)
                csv2sqlite(db, table, csv_file)
            except OperationalError as e:
                lerr.write(e.message)
                lerr.write("\n")
                msg = "SQLite error on process {} while importing '{}' : '{}'".format(process.id, input_res.url,
                                                                                      e.message)
                raise TuttleError(msg)
            finally:
                db.close()
