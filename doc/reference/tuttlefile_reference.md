# tuttlefilet reference

## syntax
A tuttlefile is made of several ``processes``.

Each process describe how to get ``output resources`` from ``input resources`` with some ``code``. A block of ``code``
is identified because every line start with the same indentation. Code can be interpreted
according to the ``processor`` chosen for the process.

For example a process producing two outputs from three inputs according to my_processor can look like that

```
scheme://output/resource/1, scheme://output/resource/2 <- scheme://input/resource/1, scheme://input/resource/2, scheme://input/resource/3 ! my_processor
    first line of code
    second line of code
```

Input and output resources are both coma separated lists of urls. An arrow ``<-`` make the separation, and empty lists
are valid.

Then comes an optional exclamation mark ``!`` with the processor name. By default, ``processor`` is ``shell`` under Linux
(and ``batch`` under windows)

Input, outputs and processor must all be on the same line (for the moment).

Also, tuttle projects can be split in several files with the ``include`` statement :

```
include load_from_databse.tuttle
```

## urls schemes

### file
``file://`` urls reference either files relatives to the tuttle file ``file://relative/path/to/file`` or an absolute path to
the file reachable from the local system ``file:///absolute/path/to/file``. Path can be either standard files or
directories.

### http - https
Any [valid http url](https://en.wikipedia.org/wiki/Web_resource), like http://github.com . Note that http resources can't be removed by tuttle, therefore invalidation of an http
resource will issue a warning. https:// is also supported.

### sqlite
A table, a view, an index or a trigger in an SQLite database. For example, a table called ``mytable``, in an SQLite
database in the file relative/path/to/sqlite_file (path is relative to the tuttlefile) has the url :
```
sqlite://relative/path/to/sqlite_file/mytable
```

Note that when tuttle removes the last table, view, index or trigger in the database, it removes the SQLite file.

### postgresql - pg:
A Postgresql resource can either be :
* a table
* a view
* a function

Url structure is :
```
pg://hostname:port/database_name/schema_name/view_or_table_name
```
where schema is optional. For example, this is a valid url from the functional tests :
```
pg://localhost:5432/tuttle_test_db/test_table
```

You can also target the schema itself :
```
pg://localhost:5432/tuttle_test_db/schema_name/
```

You can't include authentication url on purpose so that your password will never
be visible in your version control system (eg git). When running tuttle, your system user must have write access to the
database. You can either [use a ``.pgpass`` file in your user's home directory](http://www.postgresql.org/docs/9.4/static/libpq-pgpass.html)
or [set PGNAME and PGPASSWORD environnement variables](http://www.postgresql.org/docs/9.4/static/libpq-envars.html).

### Amazon S3 and compatible (experimental)
An [S3 object form AWS](https://aws.amazon.com/s3/) or compatible service. Urls are in the form :
```
s3://service_endpoint/bucket_name/key_name
```
Where ``service_endpoint`` is the server address of the service provider. The standard address for AWS is ``s3.amazonaws.com`` but
it can vary depending on [which datacenter your data is stored](http://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region). For example,
if your data is stored in Frankfurt, ``service_endpoint`` should be ``s3-website.eu-central-1.amazonaws.com``.


There are several ways to specify credentials to your account, including setting AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment
variables or creating a ``~/.aws/credentials`` configuration file. You can see the [full credential documentation](https://blogs.aws.amazon.com/security/post/Tx3D6U6WSFGOK2H/A-New-and-Standardized-Way-to-Manage-Credentials-in-the-AWS-SDKs)
for further details. Remember, you should not commit credentials to your project version control system (eg git), but have a separate way to manage your configuration.

This functionality should be considered experimental because it hasn't been properly tested on a real AWS account. Any feedback or improvement is welcome !

### Future plans
The official list of requested urls schemes available as [github issues](https://github.com/lexman/tuttle/issues?q=is%3Aopen+is%3Aissue+label%3Aprocessor)

Writing your own resources is easy if you know the python language. So consider contributing... Pull requests are
welcome !


## processors

### shell
``shell`` is the default processor on *nix systems (e.g. Linux). The code is interpreted as a shell script which stops at
the first error.

### bat
``bat`` is the default processor on windows. The code is interpreted as a batch script which stops at the first error.

### python
The ``python`` processor runs the code as a python 2.7 script

### SQLite
The ``sqlite`` processor is valid only if all input and output resources are ``sqlite://`` resources from the same
database file. The processor will run the sql code inside that database.

### PostgreSQL
The ``postgresql`` processor is valid only if all input and output resources are ``pg://`` resources from the same
database file. The processor will run the sql code inside that database.

### download
The ``download`` processor is valid only if it has one ``http://`` or ``https://`` resource as input and one ``file://``
resource as output. The processor will download the http resource and save it in the file.

### csv2sqlite
The ``csv2sqlite`` processor is valid only if it has one ``file://`` resource as input and ``sqlite://`` resource as
output. If the file is a valid CSV file, the processor will load it inside the ouput table, using the first line of
 the csv file as column names.

### Future plans
The official list of requested processors is available as [github issues](https://github.com/lexman/tuttle/issues?q=is%3Aopen+is%3Aissue+label%3Aprocessor)

NB : A lot of other magic transfer processor, like download and csv2sqlite are planned for the future

Writing your own processor is easy if you know the python language. So consider contributing... Pull requests are
welcome !
