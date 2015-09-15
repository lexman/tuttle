# tuttlefilet reference

## syntax
A tuttlefile is made of several ''processes''

Each process describe how to get ``output resources`` from ``input resources`` with some ``code``. A block of ``code``
is identified because every line start with the same indentation. Code can be interpreted
according to the ``processor`` chosen for the process.

For example a process producing two outputs from three inputs according to my_processor can look like that

```
schema:\\output\resource\1, schema:\\output\resource2 <- schema:\\input\resource1, schema:\\input\resource2, schema:\\input\resource3 ! my_processor
    first line of code
    second line of code
```

Input and output resources are both coma separated lists of urls. An arrow ``<-`` make the separation, and empty lists
are valid.

Then comes an optional exclamation mark ``!`` with the processor name. By default, ``processor`` is ``shell`` under Linux
(and ``batch`` under windows)

Input, outputs and processor must all be on the same line (for the moment).


## urls and schemas
Here is the list of urls schemas valid for tuttle

### file
file urls reference either files relatives to the tuttle file ``file://relative/path/to/file`` or an absolute path to
the file reachable from the local system ``file:\\\absolute\path\to\file``. Path can be either standard files or
directories.

### http
Any valid http url (cf rfc ??), like http://github.com . Note that http resources can't be removed by tuttle, therefore invalidation of an http
resource will issue a warning.

Note that https is not implemented yet.

### sqlite
A table, a view, an index or a trigger in an SQLite database. For example, a table called ``mytable``, in an SQLite
database in the file relative/path/to/sqlite_file (path is relative to the tuttlefile) has the url :
```
sqlite://relative/path/to/sqlite_file/mytable
```

Note that when tuttle removes the last table, view, index or trigger in the database, it removes the SQLite file.

### postgresql : pg
A table or a view, in an Postgresql database. Url structure is :
```
pg://hostname:port/database_name/schema_name/view_or_table_name
```
where schema is optional. For example, this is a valid url from the functionnal tests :
```
pg://localhost:5432/tuttle_test_db/test_schema/test_table
```

Authentication does not appear on url on purpose (even user name can be added later), so that your password will never
be visible in your version control system (eg git). When running tuttle, your system user must have write access to the
database. You can either use a ``.pgpass`` file in your user's home directory or set PGNAME and PGPASSWORD environnement
 variables. More info on [Postgresql authentication documentation](http://TODO)


## processors
