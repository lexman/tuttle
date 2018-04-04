## Processors

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
The ``download`` processor is valid only if it has one ``http://``, ``https://`` or ``ftp;//resource`` as input and one ``file://``
resource as output. The processor will download the resource and save it in the file.

### csv2sqlite
The ``csv2sqlite`` processor is valid only if it has one ``file://`` resource as input and ``sqlite://`` resource as
output. If the file is a valid CSV file, the processor will load it inside the ouput table, using the first line of
 the csv file as column names.

### Future plans
The official list of requested processors is available as [github issues](https://github.com/lexman/tuttle/issues?q=is%3Aopen+is%3Aissue+label%3Aprocessor)

NB : A lot of other magic transfer processor, like download and csv2sqlite are planned for the future

Writing your own processor is easy if you know the python language. So consider contributing... Pull requests are
welcome !
