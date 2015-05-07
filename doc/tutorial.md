# Tutorial

## A real life example
You work for this company that sells `hipstoys``. ``Hipstoys`` are the new internet things. They are wonderfull, everybody
should have oneYour company asked you to compute how well sells perform, in order publish to the intranet.

William the accountant has already mailed you a spreadshit with the number of sells per country. You found the population
of the countries somewhere in the internet, and you have written a few formulas to compute the penetration rate of
``hipstoys`` per country (``number of sales / inhabitants * 100``) and which country are far from the mean penetration
rate (more than twice the variance away from the average).


    ## screenshot here
But when you delivered the spreadshit, your boss realised the penetration rate is wrong because it is based on the
population of the country, not on the your customer targets, which are the number of internet users. And sales
will be updated next week because Paul from the Western Europe Department mixed the figures between Belgium and France.
They all thing that because computing is all automatic, as soon they've mailed the updated spreashit report will be
ready with the right figures for France and Belgium.

The purpose of this tutorial is to prove they're right : Tuttle helps you work in an real life environment where
formulas, scripts, data change all the time.

"" You can test every bit of your work with the guaranty it will all work perfectly together ""


## Get the source data on the internet

First, you need to find the number of internet users per country. After ## you notice you can't find this figure
directly but the world banck has a csv file with the percentage of people with acces to Internet per country. You can
easily join this information with the population. In an empty project directory, create a file called ``tuttlefile`` and
paste this code :

    file://internet_users.zip <- http://api.worldbank.org/v2/en/indicator/it.net.user.p2?downloadformat=csv #! download

    file://it.net.user.p2_Indicator_en_csv_v2.csv <- file://internet_users.zip
         unzip internet_users.zip it.net.user.p2_Indicator_en_csv_v2.csv


The first line tells tuttle to "download" the file from the world b:ank into internet_users.zip. The csv file we want to
use is called it.net.user.p2_Indicator_en_csv_v2.csv inside the zip, so next step is to unzip it (line 3 and 4).

Let's run this workflow, we go into the project's directory and launch ``tuttle``:

    cd demo_project
    tuttle

Tuttle checks what is missing and runs the according ``processes``, and logs the execution :

You'll be able to see the logs latter for they are available in the report. In the report you can also find the duration
of the processes, whether they have failled and their dependencies.

    ## screenshot here



