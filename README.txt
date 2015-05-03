# Tuttle : Make for data

Reliably create data from different sources.

This tool is design to help you work in team in an industrial environment... To achieve continuous data processing.

Tuttle is at a very early stage of development and must be considered as alpha, therefore Syntax is likely to change.

# Demo

A demo project can be found in https://github.com/abonnasseau/tuttle/tree/master/samples/demo

When you run this project (under Windows), you get a report of every thing that has been run, when, whether it succeeded,
 an access to the logs, and... The nice dependency graph like [this one !](http://abonnasseau.github.io/tuttle/doc/demo/tuttle_report.html)


# Install
You can find install instruction for Windows and Linux on the release page :
https://github.com/abonnasseau/tuttle/releases


# Hacking
![AppVeyor Windows build status](https://ci.appveyor.com/api/projects/status/github/tuttle)
![Travis Linux build status](https://travis-ci.org/abonnasseau/tuttle.png)

Tuttle is a python project you can download and install :

    git clone https://github.com/abonnasseau/tuttle
    cd tuttle
    python setup.py install


Contributions are very welcome through pull request. You can contribute to :
* documentation : formal doc, tutorials
* code : improve tuttle kernel, add new extensions
* tests : use Tuttle and report bugs
* syntax : help define the perfect way to describe workflows
