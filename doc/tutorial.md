# Tutorial


The purpose of this tutorial is to explain, line by line, the [demo project](examples/musketeers) which
scans the the novel *The Three Musketeers*, to measure the importance of each musketeer. From a zip archive,
you will extract the text to produce a
[png bar graph](http://abonnasseau.github.io/tuttle/docs/musketeers_assets/characters_count.png) and
a [csv file](http://abonnasseau.github.io/tuttle/docs/musketeers_assets/characters_count.csv) you can
import in our favorite spreadsheet software.

You need to have `tuttle` [installed](https://github.com/abonnasseau/tuttle/releases) on Linux, with
[gnuplot](http://www.gnuplot.info/) to run the tutorial. We'll use little python, gnuplot and shell code.

# Unzip the novel

In an empty directory, download the [zip](http://abonnasseau.github.io/tuttle/docs/musketeers_assets/Les_trois_mousquetaires.zip).
Then create a file called ``tuttlefile`` and paste this code :

    file://Les_trois_mousquetaires.txt <- file://Les_trois_mousquetaires.zip
        unzip Les_trois_mousquetaires.zip Les_trois_mousquetaires.txt

On line 1, we tell tuttle that we intend to produce Les_trois_mousquetaires.txt from the file Les_trois_mousquetaires.zip.
How to do that ? With the shell code provided on line 2 : calling online zip utility. Notice the indentation
 that delimits the code.

Let's run this workflow :

    cd demo_project
    tuttle run

Tuttle checks what is missing and runs the according *processes*, and logs the execution :

```console
lexman@lexman-pc:~/tuttle_tutorial$ tuttle run
============================================================
tuttlefile_1
============================================================
--- stdout : -----------------------------------------------
Archive:  Les_trois_mousquetaires.zip
  inflating: Les_trois_mousquetaires.txt

--- stderr : -----------------------------------------------
+ unzip Les_trois_mousquetaires.txt

```

`tuttlefile_1` is the identifier of the *process* in the *workflow* : it has been declared one line 1 of file `tuttlefile`. The
execution displays all the outputs of the process.

We have ran our first *workflow*. We can take a look at our workspace :
```console
lexman@lexman-pc:~/tuttle_tutorial$ ls -la

TODO COMPLETE HERE

lexman@lexman-pc:~/tuttle_tutorial$ head Les_trois_mousquetaires.txt

TODO COMPLETE HERE

```

Before we go on, take time to commit your work in your versioning system, eg ``git``.

# Count the number of time each musketeer appears in the text

Shell won't be enough find the words in the text. We'll use a few lines of python to parse the text and count :

    file://characters_count.dat <- file://Les_trois_mousquetaires.txt ! python
        # -*- coding: utf8 -*-
        names = ["Athos", "Porthos", "Aramis", "d'Artagnan"]
        with open('characters_count.dat', 'w') as f_out:
            with open('Les_trois_mousquetaires.txt') as f_in:
                content_low = f_in.read().lower()
            for name in names:
                name_low = name.lower()
                f_out.write("{}\t{}\n".format(name, content_low.count(name_low)))

At the end of line 1, `! python` tells tuttle to use the python *processor* to run the code of the process.

In a few words, the python code loads all the text from The Three Musketeers in memory, and converts it to lower case
to ease comparison of text. Then for each name of musketeer, it converts it in lower case it counts the occurrences in
the text, in order to write a line in file characters_count.dat.

Let's run it :

```console
lexman@lexman-pc:~/tuttle_tutorial$ tuttle run

TODO

```

You will notice tuttle only runs the necessary code. The first process `tuttlefile_1` has already run, so only the
new process `tuttlefile_3` is run.

Let's have a look at the result :

```console
lexman@lexman-pc:~/tuttle_tutorial$ cat characters_count.dat

TODO

```

Frankly, I don't have any idea if this is correct. But *d'Artagnan* is above the others, which seems appropriate.


It's time to take a look at the report. Open the file `tuttle_report.html` at the root of the workspace : you can see
everything that has happen in our workflow : duration of the processes, whether they have failed, a graph of their
dependencies. You can even download all the logs.


TODO screenshot

# Make the bar graph

Now we have data in a form that gnuplot understands. To make a graph from our data, gnuplot need this kind of program
on the standard input :

    set terminal png
    set output "characters_count.png"
    plot "characters_count.dat" using 2: xtic(1) with histogram

Tuttle does not have a gnuplot processor (... yet ! PR are welcome :), so we'll use the
[here doc](http://en.wikipedia.org/wiki/Here_document#Unix_shells) syntax to insert it in a shell process :

    file://characters_count.png <- file://characters_count.dat
    # Plot the data with gnuplot. You need to have gnuplot installed
        gnuplot <<$script$
        set terminal png
        set output "characters_count.png"
        plot "characters_count.dat" using 2: xtic(1) with histogram
        $script$


