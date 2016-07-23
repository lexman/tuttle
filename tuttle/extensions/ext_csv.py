# -*- coding: utf8 -*-
import csv
import sqlite3
import chardet
import codecs

from tuttle.error import TuttleError
from tuttle.extensions.sqlite import SQLiteResource
from tuttle.resources import ResourceMixIn, FileResource


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

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self
        
def open_csv(csv_file):
    sample = csv_file.read(1024)
    csv_file.seek(0)
    dialect = csv.Sniffer().sniff(sample)
    detect = chardet.detect(sample)
    return UnicodeReader(csv_file, dialect=dialect, encoding=detect['encoding'])


def check_csv_row(csv_reader, nb_cols):
    line_num = 2 # first line after the header
    for row in csv_reader:
        if len(row) != nb_cols:
            msg = "Wrong number of columns on line {}".format(line_num)
            raise TuttleError(msg)
        yield row
        line_num += 1


def fill_table(db, table_name, column_names, csv_reader):
    place_holders = ",".join(["?" for _ in column_names])
    columns = column_list(column_names)
    sql = "INSERT INTO `{}` ({}) VALUES ({})".format(table_name, columns, place_holders)
    db.executemany(sql, check_csv_row(csv_reader, len(column_names)))
    db.commit()


def csv2sqlite(db, table_name, csv_file):
    csv_reader = open_csv(csv_file)
    column_names = csv_reader.next()
    create_table(db, table_name, column_names)
    fill_table(db, table_name, column_names, csv_reader)


class CSV2SQLiteProcessor:
    """ A processor for Windows command line
    """
    name = 'csv2sqlite'

    def static_check(self, process):
        inputs = [res for res in process.iter_inputs()]
        outputs = [res for res in process.iter_outputs()]
        if len(inputs) != 1 \
           or len(outputs) != 1 \
           or inputs[0].scheme != 'file' \
           or outputs[0].scheme != 'sqlite':
            raise TuttleError("CSV2SQLite processor {} don't know how to handle his inputs / outputs".format(process.id))

    def run(self, process, reserved_path, log_stdout, log_stderr):
        # TODO : log queries
        # static_check ensured we know what are inputs and outputs
        input_res = process.iter_inputs().next()
        assert isinstance(input_res, FileResource)
        csv_filename = input_res._get_path()

        output_res = process.iter_outputs().next()
        assert isinstance(output_res, SQLiteResource)
        sqlite_filename = output_res.db_file
        table = output_res.objectname

        with open(log_stdout, "w") as lout, \
             open(log_stderr, "w") as lerr, \
             open(csv_filename, 'rb') as csv_file:
            db = sqlite3.connect(sqlite_filename)
            try:
                csv2sqlite(db, table, csv_file)
            except TuttleError as e:
                # Any well defined error it re-emitted as-is
                raise
            except Exception as e:
                lerr.write("Unexpected error while importing {} in SQLite database :".format(input_res._get_path()))
                lerr.write(e.message)
                lerr.write("\n")
                import traceback
                traceback.print_exc(lerr)
                msg = "SQLite error on process {} while importing '{}' : '{}. Is this file a valid CSV file ? " \
                      "More detail about the error in the error logs'".format(process.id, input_res.url, e.message)
                raise TuttleError(msg)
            finally:
                db.close()
