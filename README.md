# Tuttle : Make for data


This tool has been designed to help you create data as a team in an industrial environment, with reliability in mind.

You can change your scripts, you can merge your work with teammate's, you can checkout another branch of code, Tuttle will re-compute the data for you, but only the part that changed.
Most of all, Tuttle GUARANTIES you get the result you expect from your source files, every time you run it.


# Demo

A demo Tuttle project can be found :
* https://github.com/abonnasseau/tuttle/tree/master/samples/demo_linux for a project working under Linux
* https://github.com/abonnasseau/tuttle/tree/master/samples/demo for a project working under Windows
Have a look at the tuttlefile which describes the workflow...

When you run this project, you get a report of every thing that has been run, when, whether it succeeded,
 an access to the logs, and... The nice dependency graph like [this one !](http://abonnasseau.github.io/tuttle/docs/demo/tuttle_report.html)

Please note that Tuttle is at a very early stage of development and must be considered as alpha, therefore syntax is likely to change.


# Install
You can find install instruction for Windows and Linux on the release page :
https://github.com/abonnasseau/tuttle/releases


# Hacking
![AppVeyor Windows build status](https://ci.appveyor.com/api/projects/status/github/abonnasseau/tuttle)
![Travis Linux build status](https://travis-ci.org/abonnasseau/tuttle.png)

Tuttle is a python project you can download and install :

    git clone https://github.com/abonnasseau/tuttle
    cd tuttle
    python setup.py install


Contributions are very welcome through pull request. You can contribute to :
* documentation : formal doc, tutorials
* code : improve tuttle kernel, add new extensions
* tests : use Tuttle for your projects and report bugs
* syntax : help define the perfect way to describe workflows
