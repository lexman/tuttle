# Tutorial

## A real life example
For this tutorial, you work for this company that sells `hipstoys`` : ``Hipstoys`` are the new internet thing... They are wonderfull, everybody
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


The first line tells tuttle to "download" the file from the world bank into internet_users.zip. The csv file we want to
use is called it.net.user.p2_Indicator_en_csv_v2.csv inside the zip, so next step is to unzip it (line 3 and 4).

Let's run this workflow :

    cd demo_project
    tuttle run

Tuttle checks what is missing and runs the according ``processes``, and logs the execution :

Tuttle has created the expected file ``it.net.user.p2_Indicator_en_csv_v2.csv``. Also the file internet_users.zip is still
available. Therefore, if something wrong happens when unziping the file, you wouldn't have to download it again.

You also noticed Tuttle has logged everything that happened in the terminal. You'll be able to use the logs latter for
they are archived with in the report : tuttle has created a nice ``tuttle_report.html`` file in your workspace.
    ## screenshot here

In the report you can also find the duration of the processes, whether they have failed and their dependencies.


After such a great effort, don't forget to commit your work in your versioning system, eg ``git``. Notice that the url
of the CSV file is explicitly written in our project. It means we won't have to spend two hours on the web to find it
again, when our boss will inevitably need updated figures next year.




