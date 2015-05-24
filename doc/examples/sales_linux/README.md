# Demo : penetration rate of a product


This project [project](tuttlefile) describes a wokflow that compute the penetration rate of an internet product,
according to the sales per country, and present them in an html table. Steps are :

* download some files about population and internet from the world bank
* unzip them
* put both tabular files in a sqlite database
* join the figures with `sales.tsv` to compute how well sales relate to the number of internet users per country
* insert the data in an html template for rendering through a python script

When you run this project, you get a [report](http://abonnasseau.github.io/tuttle/docs/demo/tuttle_report.html) of every
thing that has been run, when, whether it succeeded, an access to the logs, and... A nice dependency graph !

