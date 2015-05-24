# Tuttle : Make for data


This tool has been designed to help you create data as a team in an industrial environment, with reliability in mind.

Whether you change the scripts, merge your work with teammate's, checkout another branch of code, Tuttle will re-compute the data for you, but only the part that changed.
Most of all, Tuttle GUARANTIES the result you expect from your source files, every time you run it, onn every plateform.


# Syntax

Here's an example of the syntax of tuttle : this projects aims a findind the importance of
each musketeer in the novel *The Three Musketeers*. It should produce a png bar graph and 
a csv file you can import in our favorite spreadsheet software :

	file://words.txt <- file://Les_trois_mousquetaires.txt
		# Exctract all the words from the book "The Three Musketeers", each word on a line
		awk '{for(i=1;i<=NF;i++) {print $i}}' Les_trois_mousquetaires.txt > words.txt

	file://characters.txt <- file://words.txt
		# Keep only the lines with the names of the musketeers
		grep -e Athos -e Portos -e Aramis -e "d'Artagnan" words.txt > characters.txt
		
	file://characters_count.dat <- file://characters.txt
		# Creates a .dat file for ploting with gnuplot
		sort characters.txt | uniq -c > characters_count.dat

	file://characters_count.csv <- file://characters_count.dat
		# Creates a file readable by a spreasheet software : 
		# * add quotes around the name of the character
		# * add Windows style new lines
		awk '{print "\""$2"\","$1"\r"}' characters_count.dat > characters_count.csv
		
	file://characters_proportion.png <- file://characters_count.dat
		# Plot the data
		gnuplot <<$script$
		set terminal png
		set output "characters_proportion.png"
		plot "characters_count.dat" using 1: xtic(2) with histogram
		$script$

This project does not produce the rigth answer on purpose. Coming soon : a tuttorial showing how to fix errors.

# Demo

A demo Tuttle project is available [under Windows](https://github.com/abonnasseau/tuttle/tree/master/samples/demo) and
 and [under Linux](https://github.com/abonnasseau/tuttle/tree/master/samples/demo_linux). It consist of a ``tuttlefile`` that
 describe a whole workflow of processing :
* download some files about population and internet from the world bank
* unzip them
* stuff them in a sqlite database
* join the figures with a ``sales.tsv`` to compute how well sales relate to the number of internet users per country
* insert the data in an html template for rendering (through a python script)

When you run this project, you get a [report](http://abonnasseau.github.io/tuttle/docs/demo/tuttle_report.html) of every thing that has been run, when, whether it succeeded,
 an access to the logs, and... A nice dependency graph !

Please note that Tuttle is at a very early stage of development and must be considered as alpha, therefore syntax as
well as command line options are likely to change.


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
* code : improve tuttle kernel, add new extensions : spreadshits, mongodb, hdfs, etc.
* tests : use Tuttle for your projects and report bugs
* syntax : help define the perfect way to describe workflows
* design : please help us improve the look of the [report](http://abonnasseau.github.io/tuttle/docs/demo/tuttle_report.html) to ease readability !
