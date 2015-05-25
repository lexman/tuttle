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

```console
lexman@lexman-pc:~$ cd tuttle_tutorial
lexman@lexman-pc:~/tuttle_tutorial$ tuttle run
============================================================
tuttlefile_1
============================================================
--- stdout : -----------------------------------------------
Archive:  Les_trois_mousquetaires.zip
  inflating: Les_trois_mousquetaires.txt

--- stderr : -----------------------------------------------
+ unzip Les_trois_mousquetaires.txt
lexman@lexman-pc:~/tuttle_tutorial$
====
Done
```

`tuttlefile_1` is the identifier of the *process* in the *workflow* : it has been declared one line 1 of file `tuttlefile`. The
execution displays all the outputs of the process.

We have ran our first *workflow*. We can take a look at our workspace :

```console
lexman@lexman-pc:~/tuttle_tutorial$ ls -la
total 1854
drwxrwx--- 1 lexman lexman    4096 mai   25 22:59 .
drwxrwx--- 1 lexman lexman    4096 mai   25 22:51 ..
-rwxrwx--- 1 lexman lexman 1389543 mai   24 20:27 Les_trois_mousquetaires.txt
-rwxrwx--- 1 lexman lexman  495538 mai   24 20:36 Les_trois_mousquetaires.zip
drwxrwx--- 1 lexman lexman       0 mai   25 22:57 .tuttle
-rwxrwx--- 1 lexman lexman     785 mai   25 23:00 tuttlefile
-rwxrwx--- 1 lexman lexman    3837 mai   25 22:59 tuttle_report.html

lexman@lexman-pc:~/tuttle_tutorial$ head Les_trois_mousquetaires.txt
PRÉFACE

dans laquelle il est établi que malgré leurs noms en os et en is, les héros de l'histoire que nous allons avoir l'honneur de raconter à
[...]
capricieux du poète n'est pas toujours ce qui impressionne la masse des lecteurs. Or, tout en admirant, comme les autres les admireront sans doute, les détails que nous avons signalés, la chose qui nous préoccupa le plus est une chose à laquelle bien certainement personne avant nous n'avait fait la moindre attention.
lexman@lexman-pc:~/tuttle_tutorial$
```

Well, the text is in french, but it does look like a novel, as we expected.

Now we go on, take time to commit your work in your versioning system, eg ``git``.

# Count musketeers

Shell won't be enough find the words in the text. We'll use a few lines of python to parse the text and count :

file://characters_count.dat <- file://Les_trois_mousquetaires.txt !# python
    # -*- coding: utf8 -*-
    names = ["Athos", "Porthos", "Aramis", "d'Artagnan"]
    with open('characters_count.dat', 'w') as f_out:
        with open('Les_trois_mousquetaires.txt') as f_in:
            content_low = f_in.read().lower()
        print("{} chars in the novel".format(len(content_low)))
        for name in names:
            name_low = name.lower()
            f_out.write("{}\t{}\n".format(name, content_low.count(name_low)))
            print("{} - done".format(name))

At the end of line 1, `! python` tells tuttle to use the python *processor* to run the code of the process.

In a few words, the python code loads all the text from The Three Musketeers in memory, and converts it to lower case
to ease comparison of text. Then for each name of musketeer, it converts it in lower case it counts the occurrences in
the text, in order to write a line in file characters_count.dat.

Let's run it :

```console
lexman@lexman-pc:~/tuttle_tutorial$ tuttle run
============================================================
tuttlefile_4
============================================================
--- stdout : -----------------------------------------------
1389543 chars in the novel
Athos - done
Porthos - done
Aramis - done
d'Artagnan - done
====
Done
lexman@lexman-pc:~/tuttle_tutorial$
```

You will notice tuttle only runs the necessary *processes* : The first process `tuttlefile_1` has already run, so only the
new process `tuttlefile_4` is executed.

Let's have a look at the result :

```console
lexman@lexman-pc:~/tuttle_tutorial$ cat characters_count.dat
Athos	971
Porthos	590
Aramis	526
d'Artagnan	1864
lexman@lexman-pc:~/tuttle_tutorial$
```

Frankly, I don't have any idea if this is correct. But *d'Artagnan* is above the others, which seems coherent with the
him being the hero of the novel.


It's time to take a look at the report. Open the file [`tuttle_report.html`](http://abonnasseau.github.io/tuttle/docs/musketeers_tutorial_assets/count_musketeers/tuttle_report.html) at the lexman of the workspace : you can see
everything that has happen in our workflow : duration of the processes, whether they have failed, a graph of their
dependencies. You can even download all the logs.


# Make the bar graph

Now we have data in a form that gnuplot understands. To make a graph from our data, gnuplot need this kind of program
on the standard input :

    set terminal png
    set output "characters_count.png"
    plot "characters_count.dat" using 2: xtic(1) with histogram

Tuttle does not have a gnuplot processor (... yet ! PR are welcome :), so we'll use the
[here doc](http://en.wikipedia.org/wiki/Here_document#Unix_shells) syntax to insert it in a standard shell *process* :

    file://characters_count.png <- file://characters_count.dat
        gnuplot <<$script$
        set terminal png
        set output "characters_count.png"
        plot "characters_count.dat" using 2: xtic(1) with histogram
        $script$

After we've ran tuttle, we can see the [graph](http://abonnasseau.github.io/tuttle/docs/musketeers_assets/characters_count.png) !

It's time to commit our work once again.

# Export to spreadsheet

When you work on data, there is always someone who's interested about what you're doing. He wants the raw figures to
make his own presentation.

In our case, this means we have to translate our .dat file into a csv compatible with his
spreadsheet software : we have to quote the text, and values must be separated by a coma instead of a tabulation...
And Windows style newlines !

A simple line of awk do the trick :

    file://characters_count.csv <- file://characters_count.dat
        awk '{print "\""$1"\","$2"\r"}' characters_count.dat > characters_count.csv

After we've run the workflow, we get exactly what we expected :

    971,"Athos"
    590,"Porthos"
    526,"Aramis"
    1864,"d'Artagnan"

Now if change anything in our workflow, the csv file will be updated along with the rest. So we can send the update
right away !

# Conclusion
We've seen how to run a process with tuttle. In the incoming tutorial, you will learn how to deal with errors while you
work.