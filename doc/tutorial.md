# Tutorial

## A real life example
For this tutorial, you work for this company that sells ``hipstoys``... ``Hipstoys`` are the new internet thing : they are wonderful, everybody
should have one ! Your company asked you to compute how well sells perform, in order publish a report to the intranet.

William, the accountant, has already mailed you a spreadsheet with the number of sells per country. You found the population
of the countries somewhere in the internet, and you have written a few formulas to compute the penetration rate of
``hipstoys`` per country (``number of sales / inhabitants * 100``) and which country differ from the mean penetration
rate (more than twice the variance away from the average).


    ## screenshot here
But when you delivered the spreadsheet, your boss realised the penetration rate is wrong because it is based on the
population of the country... Not on the the number of internet users : your real target. And the sales spreadsheet
will be updated next week because Maurice from the Western Europe Department mixed the figures between Belgium and France.

Of course he thinks that because computing is all automatic, as soon has mailed the updated spreadsheet report will be
ready with the right figures for France and Belgium.

The purpose of this tutorial is to prove he's right : Tuttle helps you work efficiently in an real life environment where
formulas, scripts, data change all the time.

"" You can test every bit of your work with the guaranty it will all work perfectly together ""


## Retrieve the source data from the internet

First, you need to find the number of internet users per country. After ## you notice you can't find this figure
directly but the world bank has a csv file with the percentage of people with access to Internet per country. You can
easily join this information with the population.

In an empty project directory, create a file called ``tuttlefile`` and paste this code :

    file://internet_users.zip <- http://api.worldbank.org/v2/en/indicator/it.net.user.p2?downloadformat=csv #! download

    file://it.net.user.p2_Indicator_en_csv_v2.csv <- file://internet_users.zip
         unzip internet_users.zip it.net.user.p2_Indicator_en_csv_v2.csv


The first line tells tuttle to ``download`` the file from the world bank into internet_users.zip. The csv file we want to
use is called it.net.user.p2_Indicator_en_csv_v2.csv inside the zip, so next step is to unzip it (line 3 and 4).

#TODO explain more


Let's run this workflow :

    cd demo_project
    tuttle run

Tuttle checks what is missing and runs the according ``processes``, and logs the execution :

```console
lexman@lexman-pc:~/tuttle_tutorial$
============================================================
tuttlefile_1
============================================================
--- stdout : -----------------------------------------------
Downloading http://api.worldbank.org/v2/en/indicator/it.net.user.p2?downloadformat=csv
..
done

============================================================
tuttlefile_3
============================================================
--- stdout : -----------------------------------------------
Archive:  internet_users.zip
  inflating: it.net.user.p2_Indicator_en_csv_v2.csv

--- stderr : -----------------------------------------------
+ unzip internet_users.zip it.net.user.p2_Indicator_en_csv_v2.csv

````

Tuttle has created the expected file ``it.net.user.p2_Indicator_en_csv_v2.csv``. Also the file internet_users.zip is still
available. Therefore, if something wrong happens when unziping the file, you wouldn't have to download it again.

We can se execution of process `tuttlefile_3` (process defined at line 3 of file tuttlefile)

You also noticed Tuttle has logged everything that happened in the terminal : for example, process `tuttlefile_3` (process
defined at line 3 of file `tuttlefile`), displays the details of what the zip command traces to stdout and stderr.

You'll also be able to use the logs latter for they are archived with in the report : tuttle has created a nice ``tuttle_report.html`` at the root of your workspace.
    ## screenshot here

In the report you can also find the duration of the processes, whether they have failed and their dependencies.


After such a tremendous effort, don't forget to commit your work in your versioning system, eg ``git``. Notice that the url
of the CSV file is explicitly written in our project. It means we won't have to spend two hours on the web to find it
again, when our boss will inevitably need updated figures next year.


## Insert the data into sqlite

A pleasant way join the data from the different sources is using SQL, which is an easy language to process structured
 data. Therefore we will insert all the data into an SQLite database, starting by the number of sells received by mail.
After converting the spreadsheet to a proper tabular file, we save it in our workspace. Then we can add this line to our
`tuttlefile` :

    sqlite://stats.sqlite/tables/sales <- file://sales.tsv #! csv2sqlite


csv2sqlite is a specific *processor* that understands it has to transfer the data from a tabular file (comma delimited
 or tabular) in input (sales.csv) into an sqlite table (table `sales` in database `stats.sqlite`). Column names are
 extracted from the first line of the file.


Let's ``tuttle run`` again :

```console
Code will go here
````

A the former part of our workflow has already been executed, tuttle only runs this last line.

Let's also do this for the csv file we have downloaded earlier :

        sqlite://stats.sqlite/tables/wb_internet_users <- file://it.net.user.p2_Indicator_en_csv_v2.csv #! csv2sqlite

And `tuttle run` :

```console
Code will go here
````

Ouch ! Something went wrong. Let's have a look at the csv files ``head it.net.user.p2_Indicator_en_csv_v2.csv`` :

```console
Code will go here
````

The files contains two extra lines before the headers. We'll have to remove them before loading the data into SQLite, so we
**replace** the former line by these ones :

    file://wb_internet_users_2013.tsv <- file://it.net.user.p2_Indicator_en_csv_v2.csv
        tail -n +3 it.net.user.p2_Indicator_en_csv_v2.csv > wb_internet_users_2013.tsv

    sqlite://stats.sqlite/tables/wb_internet_users <- file://wb_internet_users_2013.tsv #! csv2sqlite

This means file `wb_internet_users_2013.tsv` is produced from file `it.net.user.p2_Indicator_en_csv_v2.csv` by running
the shell command `tail` which extracts everything from it.net.user.p2_Indicator_en_csv_v2.csv, starting on line 3.

Let's `tuttle run`:

```console
Code will go here
````

The newer workflow worked this time. Notice that tuttle has only produced the needed part. It has even automatically
cleaned up what is no longer needed from the former workflow !



Don't worry for the duplication of data between files `wb_internet_users_2013.tsv` and `it.net.user.p2_Indicator_en_csv_v2.csv` :
nowadays disk space is cheap and your time as data expert has much more value than a few bits.


Once again, we'll commit our work : `tuttlefile` and `sales.tsv`. We achieved to move the value of our work not in the final
data any more but in the description of how to produce it : anyone who wants the final data can easily checkout the repository
and run tuttle to get it in a few cpu cycles.


## Join tables to compute the number of internet users

It's time to get to the fun part : now that we have all our data in SQLite, let's do a few queries to build our data. First,
we are going to create a table with the number of internet users per country, from both the population and percentage of internet users.


This table will be called nb_internet_users :

    sqlite://stats.sqlite/tables/nb_internet_users <- sqlite://stats.sqlite/tables/wb_internet_users, sqlite://stats.sqlite/tables/world_population #! sqlite
        CREATE TABLE nb_internet_users AS
        SELECT
            wb_internet_users.`Country Name` AS country_name,
            wb_internet_users.`Country Code` AS country_code,
            wb_internet_users.`2013` as pct_internauts,
            world_population.`2013` as population,
            CAST(wb_internet_users.`2013` * world_population.`2013` / 100 AS INT) as nb_internauts
        FROM wb_internet_users LEFT JOIN world_population ON wb_internet_users.`Country Code` = world_population.`Country Code`

