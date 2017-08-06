# News
July 6th : Version 0.5 Release Candidate 1 is [available](https://github.com/lexman/tuttle/releases/tag/v0.5-rc1) !

# Tuttle : Make for data


This tool has been designed to help you create data as a team in an industrial environment, with reliability in mind.

Whether you change the scripts, merge your work with teammate's, checkout another branch of code, Tuttle will re-compute the data for you, but only the part that changed.
Most of all, Tuttle GUARANTIES the result you expect from your source files, every time you run it, onn every plateform.


# Syntax

Here's an example of the syntax of tuttle : this projects aims a finding the importance of
each musketeer in the novel *The Three Musketeers*. The text has to be extracted from a zip file,
and the whole workflow should produce a png bar graph and a csv file you can import in our favorite
spreadsheet software :

    file://Les_trois_mousquetaires.txt <- file://Les_trois_mousquetaires.zip
    # extracts the text of the novel from the archive
        unzip Les_trois_mousquetaires.zip Les_trois_mousquetaires.txt

    file://characters_count.dat <- file://Les_trois_mousquetaires.txt ! python
    # reads the text and counts the occurrences of each musketeer (comparisons
    # are made in lower case to avoid surprises !)
        # -*- coding: utf8 -*-
        names = ["Athos", "Porthos", "Aramis", "d'Artagnan"]
        with open('characters_count.dat', 'w') as f_out:
            with open('Les_trois_mousquetaires.txt') as f_in:
                content_low = f_in.read().lower()
            for name in names:
                name_low = name.lower()
                f_out.write("{}\t{}\n".format(name, content_low.count(name_low)))

    file://characters_count.csv <- file://characters_count.dat
    # Creates a file readable by a spreadsheet software :
    # * add quotes around the name of the character
    # * add Windows style new lines
        awk '{print "\""$1"\","$2"\r"}' characters_count.dat > characters_count.csv

    file://characters_count.png <- file://characters_count.dat
    # Plot the data with gnuplot. You need to have gnuplot installed
        gnuplot <<$script$
        set terminal png
        set output "characters_count.png"
        plot "characters_count.dat" using 2: xtic(1) with histogram
        $script$


When you run this project, you get a [report](http://lexman.github.io/tuttle/docs/examples/musketeers_tuttle_dir/report.html) of every
thing that has been run, when, whether it succeeded, an access to the logs, and... A nice dependency graph !

![Dependency graph](doc/screenshot_report.png)

You'll find details on this workflow on the dedicated [tutorial](doc/tutorial_musketeers/tutorial.md).

Please note that Tuttle is at a very early stage of development and must be considered as alpha, therefore syntax as
well as command line options are likely to change.


# Install
You can find [download tuttle](https://github.com/lexman/tuttle/releases) and install it on your system :

* on Windows, download the .msi installer
* on debian and ubuntu a .deb is provided
* on other systems, you need to install [python 2.7](https://www.python.org/downloads/release) and install tuttle from the sources :
```
    git clone https://github.com/lexman/tuttle
    cd tuttle
    python setup.py install
```

# Hacking


[![AppVeyor Windows build status](https://ci.appveyor.com/api/projects/status/github/lexman/tuttle)](https://ci.appveyor.com/project/lexman/tuttle)
[![Travis Linux build status](https://travis-ci.org/lexman/tuttle.png)](https://travis-ci.org/lexman/tuttle)

Tuttle is a python project you can download and install :

    git clone https://github.com/lexman/tuttle
    cd tuttle
    python setup.py install



Contributions are very welcome through pull request. You can contribute to :
* documentation : formal doc, tutorials
* code : improve tuttle kernel, add new extensions : spreadshits, mongodb, hdfs, etc. Code have to come with tests and documentation
* tests : use Tuttle for your projects and report bugs
* syntax : help define the perfect way to describe workflows
* design : please help improve the look of the [report](http://lexman.github.io/tuttle/docs/sales_assets/tuttle_report.html) to ease readability !
