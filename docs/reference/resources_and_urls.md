# Resources and urls
tuttle allows you to create and access a wide  variety of data, not only files, but resources over the internet or in your cluster, as long as you can descrie it with an url.
tuttle implements several common type of resources :

## file
``file://`` urls reference either files relatives to the tuttle file ``file://relative/path/to/file`` or an absolute path to
the file reachable from the local system ``file:///absolute/path/to/file``. Path can be either standard files or
directories.

## http - https
Any [valid http url](https://en.wikipedia.org/wiki/Web_resource), like http://github.com . Note that http resources can't be removed by tuttle, therefore invalidation of an http
resource will issue a warning. https:// is also supported.

## ftp
Any ftp file or directory, like ftp://ftp.debian.org/debian/README. Like every other resources, you can [set authentication](resources_authentication.md)) to
the ftp server. They can be downloaded (not uploaded) with the download processor.

## sqlite
A table, a view, an index or a trigger in an SQLite database. For example, a table called ``mytable``, in an SQLite
database in the file relative/path/to/sqlite_file (path is relative to the tuttlefile) has the url :
```
sqlite://relative/path/to/sqlite_file/mytable
```

Note that when tuttle removes the last table, view, index or trigger in the database, it removes the SQLite file.

## postgresql - pg:
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

## Amazon S3 and compatible (experimental)
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

## odbc
Any table or partition from a table in a database with an odbc connector. Assuming your table is called ``my_table``, and the database is available with Data
Source Name ``datasource_name``, the url would be :
````
odbc://datasource_name/my_table
````
ODBC resources have experimental support for partitioning, which means you write chunks of data according to a filter on columns. If your column is "my_col" , this is a valid url :
````
odbc://datasource_name/my_table?my_col=a_value
````
Only one set of filters is allowed for the same table.

## hdfs
Any file or directory in an hdfs storage. eg ``hdfs:\\myserver\path\to\my\file``

## Future plans
The official list of requested urls schemes available as [github issues](https://github.com/lexman/tuttle/issues?q=is%3Aopen+is%3Aissue+label%3Aprocessor)

Writing your own resources is easy if you know the python language. So consider contributing... Pull requests are
welcome !
