New on Version 0.5
===

## Parallelism
* Tuttle can now run several processes in parallel in respect to dependency order. For example, ``tuttle run --jobs 2`` will run your workflow with two workers. Default is still 1.
* Live logs : you don't need anymore to wait until a process is complete to see the logs anymore. As soon as a line is complete it is displayed.
* With ``--keep-going`` option, ``tuttle run`` doesn't stop at first error but tries to process as much as it can. Thus multiple failures *can* occur. Also running a failing process with ``keep-going`` will try to run all remaining processes


## Other
  * New ``check-integrity`` option validates that no resource have changed since tuttle have produced them
  * Two processes without outputs can't have exactly the same inputs because we can't make the difference between them
  * Error message in report for failing (pre-)processes
  * Version in report and in dumps so we can remember with which tuttle the data was crafted
  * Interrupting tuttle with ^C will set running processes in error as **aborted**

## Internals
  * Major refactoring of the invalidation system in order to make it easier to reason about
  * Only one call to ``exists()`` per resource and per run, because checking if an external piece of exist can be long. Also ``signature()`` is call maximum once because it can be *very* long

## Bug fixes
  * Invalidation is now coherent for a processes without outputs : once it have succeeded, it won't run again
  * Fixed persistence of logs in the ``.tuttle`` directory when a process id changes (ie : when its position change in the tuttlefile)
  * Running tuttle with a postgresql resource will fail with explaination before running processes if it can't connect to the database instead of saying that resources don't exists
  * ```--threshold`` now take into account duration of processes that don't create outputs


New on Version 0.4
===

## Parametric processes
... To describe a workflow according to a configuration file or a the content of a directory :
  * 'preprocesses' are run before the workflow is executed
  * you can add processes to a workflow with the new command ``tuttle-extend-workflow`` from a preprocesses
  * a new tutorial explains how it works in detail

## Other
  * coma is DEPRECATED to separate resources in dependency definitions. You should now use space instead
  * [docker images](https://hub.docker.com/r/tuttle/tuttle/) are available to use tuttle

## Bug fixes
  * escape process ids in the report
  * ``file://`` is not a valid resource
  * ``!shell`` does not stand for processor ``hell``


  
New on Version 0.3
===

## New "include" statement
... To split a tuttle project in several files

## More documentation
the reference lists all the resources and processors available

## New resources and processors :
  * PostgreSQL tables, views, functions and index resources
  * PostgreSQL Processor
  * https resources
  * AWS s3 resources (experimental)

## Better tests
Part of tuttle's job is to connect to third party tools. Integration tests must cover these tools, like Postgresql or a web server... Two methods have been developed :
  * mock the third party tool with some python code (web server, s3 server)
  * use the third party tool if it is installed on the machine (postgresql)

## A few bug fixes
  * bug on install that required jinja2 before installing dependencies

New on Version 0.2
===

## New resources and processors :
  * SQLite tables, views, triggers and index resources
  * SQLite Processor
  * http resources
  * download processor
  * Pyton Processor

## A few bug fixes

## And a tutorial as the first step to the doc !


V0.1 : first official release
===
The goal of 0.1 is to show the intended usage of tuttle, in term of command line workflow.