When crafting some data from other data, like packaging public data 

using the good tool can make the difference. As advocated by Mike Bostock's in his [blog](https://bost.ocks.org/mike/make/) 
one good tool is the venerable ``make`` that have been used for decades to build software. 

Let's take an example with [geo-countries](http://github.com/datasets/geo-countries) datapackage. To craft it we have to download data 
from NaturalEarth, extract the zip, convert it to json with ogr, the ''swiss-army-knife'' of maps, and rename a column.

Following Mike Bostok's advice, here's a ``Makefile`` we can write :

    all: ../data/countries.geojson
    
    ne_10m_admin_0_countries.zip:
        wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip

    ne_10m_admin_0_countries.README.html ne_10m_admin_0_countries.VERSION.txt ne_10m_admin_0_countries.dbf ne_10m_admin_0_countries.prj ne_10m_admin_0_countries.shp ne_10m_admin_0_countries.shx: ne_10m_admin_0_countries.zip
        unzip ne_10m_admin_0_countries.zip

    ne_10m_admin_0_countries.geojson: ne_10m_admin_0_countries.dbf ne_10m_admin_0_countries.prj ne_10m_admin_0_countries.shp ne_10m_admin_0_countries.shx
        ogr2ogr -select admin,iso_a3  -f geojson ne_10m_admin_0_countries.geojson ne_10m_admin_0_countries.shp
        
    ../data:
        cd ..
        mkdir data

    ../data/countries.geojson: ne_10m_admin_0_countries.geojson ../data
    # Change the name of the fields after conversion
        cat ne_10m_admin_0_countries.geojson | sed 's/"admin": /"name": /g' | sed 's/"iso_a3": /"ISO3166-1-Alpha-3": /g'  > ../data/countries.geojson


If you're not familiar with Makefiles, the last section reads : "When both files ``ne_10m_admin_0_countries.geojson`` and ``../data`` are be available, you can run command ``cat ne_10m_admin_0_countries.geojson | sed 's/"admin": /"name": /g' | sed 's/"iso_a3": /"ISO3166-1-Alpha-3": /g'  > ../data/countries.geojson``
and it will produce file ``../data/countries.geojson``". Make deduces the commands to be run, start with the ones where everything is available, until it produces **target** ``all``.

    
    
We achieve two very important goals with this ``Makefile`` :
* it covers the whole process even the download part. It's so easy to forget weather we have downloaded ``ne_10m_admin_0_countries.zip`` or 
``ne_110m_admin_0_countries.zip`` when it is done by hand. But now every thing is written down so we can keep track of it in our source repository (like git)
* Running ``make`` checks the date consistency of the files. That means that if we are in 2015 and Scottland has just gone independent (hasn't it ?), creating 
a new country, I can download the updated version of ``ne_10m_admin_0_countries.zip``. When running ``make`` again, it would notice that the unziped files 
like ``ne_10m_admin_0_countries.README.html`` and so on are older than their source, so the ``unzip`` command has to be run again ! And so on because 
``ne_10m_admin_0_countries.geojson`` would not be up to date, until every depending file is updated.


Even if this is a great improvement over **running all the commands manually and don't remember them** and **custom script that must start from scratch each time**, 
it is not enough to have a fluid and reliable development experience. That's the purpose of ''tuttle''. Before we se in detail two major improvements, let's see 
the same workflow written in a tuttlefile :


    file://ne_10m_admin_0_countries.zip <- http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip
        wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip

    file://ne_10m_admin_0_countries.README.html, file://ne_10m_admin_0_countries.VERSION.txt, file://ne_10m_admin_0_countries.dbf, file://ne_10m_admin_0_countries.prj, file://ne_10m_admin_0_countries.shp, file://ne_10m_admin_0_countries.shx <- file://ne_10m_admin_0_countries.zip
        unzip ne_10m_admin_0_countries.zip

    file://ne_10m_admin_0_countries.geojson <- file://ne_10m_admin_0_countries.dbf, file://ne_10m_admin_0_countries.prj, file://ne_10m_admin_0_countries.shp, file://ne_10m_admin_0_countries.shx
        ogr2ogr -select admin,iso_a3  -f geojson ne_10m_admin_0_countries.geojson ne_10m_admin_0_countries.shp
        
    file://../data <-
        cd ..
        mkdir data
        
    file://../data/countries.geojson <- file://ne_10m_admin_0_countries.geojson, file://../data
    # Change the name of the fields after conversion
        cat ne_10m_admin_0_countries.geojson | sed 's/"admin": /"name": /g' | sed 's/"iso_a3": /"ISO3166-1-Alpha-3": /g'  > ../data/countries.geojson

Looks familiar ?


Well, there are a lot of urls... That's because ``tuttle`` aims at giving a url to every bit of data, to link them together.

You can see the main difference with the former ``Makefile`` is the first section of the tuttlefile clearly states the dependency of file ``ne_10m_admin_0_countries.zip`` to url ``http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip``. 
This means that when the list of countries change, no extra manual action is required. You just have to execute the same command as if you where
building the data for the first time :``tuttle run``. It will notice the source url has changed and will update the data accordingly.



The other difference with ``make`` is not in the syntax, it's in how it deals with changes in the `tuttlefile``. If you ever worked with the ``ogr2ogr``
tool, you know it's impossible to make it right the first time. But if you happen to change the ``ogr2ogr`` command in a make file, unfortunately running
``make`` won't update the data because the modification date of the files seem coherent. 
Whereas in tuttle is made to watch for changes in the command. When you run it, it will first clean up
whatever data had been produced the previous time, and will re-run the updated ogr2ogr command. That's very handy when prototyping because you wan focus on your code
without side effects caused by remaining data. 
The other advantage
is when you work in a team. We've already seen that with ``make``, if you have changed the makefile, you need to send a mail to all your team with instructions of how to clean 
the workspace (ie : "Please remove file ../data/countries.geojson because I have changed the ogr2ogr command"), and hope nobody misses it because it would lead to 
undebuggable behaviour. 
With ``tuttle`` you can safely share or merge changes with your fellow contributors.


Now, if you put both improvements over ``make`` together (remote dependencies and reliably reprocess what have changed), we'll be able to set up a system that 
automatically updates datapackages when the source changes, and warn us only if it has failed. Pretty cool, huh ?


If you are curious about the potential of tuttle for crafting data after reading this artcle, the best way to learn more (sugar syntax, urls to data 
bases, inlined languages) is to read the tutorial.



``tuttle`` aims at giving a url to every bit of data, that way, it can connect them
comment-for-debug pattern
commentaires

tuttle cleans up