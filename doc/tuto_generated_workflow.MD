# Extend a workflow with your favorite language

This tutorial assumes you are already familiar with ``tuttle`` and you already understand the main tutorial. But you've been stuck in a use case : you 
don't know all your inputs... It could be either because you want to process a list of files, or because your workflow depends on a configuration file
you can only get with custom code.

We'll use the first case a an example. Let's assume we want to publish a list of images to the web, and we want to resize them
with [imgagemagick](http://www.imagemagick.org/), add my avatar from github to identify property, and allow the user to download
the photo with the original size.

First, the way to get the avatar and resize it to 100x100 if very classic. Here's our ``tuttlefile`` :

    file://avatar.jpg <- https://avatars.githubusercontent.com/u/2512784 ! download

    file://avartar100x100.jpg <- file://avatar.jpg
    # Use imagemagick to resize the avatar
        convert avatar.jpg -resize 100x100 avatar100x100.jpg

We can store it on the ``src`` directory of our project. Then we can run tuttle in the src directory and see everything works fine :

    cd src
    tuttle run

You should see ![me](https://avatars.githubusercontent.com/u/2512784) in your project directory :)


Now that's done,lLet's have a look at the overall structure of the sources our project :
    src/                -> the tuttle source and utility files
        tuttlefile      -> the main project file
        img_index.html  -> the index.html for each image
        ...             -> some other files we'll need
    images/             -> the original input images
        IMG_001.jpg
        IMG_002.jpg
        ...
    web/                -> the directory where we want to create the web site described above

The ``src`` directory will have all the need files to run the tuttle project. All the original images we have to process
 will be in the ``images`` directory, and the result will go in the ``web`` directory. We'll only have to copy the
 directory to our web server to put it online.

The web site should consist of an index with the thumbnails of the photos and a directory per photo with an index, a small
size photo to be displayed by the index, and the photo to download, as we can see here :

    index.html          -> the main html page with the list of images
    IMG_001.jpg/        -> the directory for presenting IMG_001.jpg to the user
        index.html      -> the html index to display IMG_001 and show the download link
        img_800x600.jpg -> the image reduced to 800x600
        img.jpg         -> the original image to download
    IMG_002.jpg/        -> the directory for presenting IMG_001.jpg to the user
        index.html      -> the html index to display IMG_001 and show the download link
        img_800x600.jpg -> the image reduced to 800x600
        img_download.jpg         -> the original image to download
    IMG_.../            -> and so on for every image...
    thumbnails/
        IMG_001.jpg     -> 200x150 thumbnail for IMG_001 with a white frame
        IMG_002.jpg     -> 200x150 thumbnail for IMG_002 with a white frame
        ...             -> and so on for every image

For a picture in the ``images`` path, we need to create a subdirectory in the web directory and create the
download image. My small avatar should appear on the bottom left corner of the image. In order to do that, we'll
create a ``src/img.tpl.tuttlefile`` file that will have all the tuttle code for one image :


    file://../web/{{img}} <- file://../images/{{img}}
    # creates the directory for the web page presenting the photo
        mkdir ../web/{{img}}

    file://../web/{{img}}/{{img}} <- file://../images/{{img}}, file://../web/{{img}}
    # add the avatar to the bottom left corner of the image and stores it to the web site
        composite -gravity SouthEast avatar100x100.jpg ../images/{{img}} ../web/{{img}}/{{img}}

As you can see, the {{img}} parameter represents the name of the image from the ``images/`` directory. The whole
file uses the [jinja2](http://jinja.pocoo.org/) syntax to inject variables like ``img`` in the tuttlefile.

How to inject the variable for each image ?

The previous file is not a valid tuttlefile and can not be run as is. We have to add two lines in the end of the
tuttlefile in order to apply the previous snippet to the first file in our image directory : IMG_001.jpg

    file://avatar.jpg <- https://avatars.githubusercontent.com/u/2512784 ! download

    file://avartar100x100.jpg <- file://avatar.jpg
    # Use imagemagick to resize the avatar
        convert avatar.jpg -resize 100x100 avatar100x100.jpg

    |<<
        tuttle-extend-workflow img.tpl.tuttlefile img=IMG_001.jpg

The last two lines in the main tuttlefile declares a *preprocess*. As the symbol ``|<<`` suggests (it should look
like a rewind button !), this code will be executed *before* the whole workflow is run.

Therefore you can add some extra processes to the main workflow (with the tuttle-extend-workflow command), which
injects the ``img`` variable into the template we wrote.

Actually, anyone familiar with the ``for`` syntax in shell can create new part of the process for
every image :

    |<<
        for img_file in `ls images`
        do
           tuttle-extend-workflow img.tpl.tuttlefile img=$img_file
        done

Let's ``tuttle run`` this workflow. We can see the dependency graph show the new processes :

[IMG]

Note that all the preprocesses are run once and for all before trying to run the workflow. This means tuttle can
still make some *static* analysis on the workflow to detect missing resources, wrong definitions or circular
references, but only once the processes are known.

For example let's ``tuttle run`` again :

    RESUlT


As we can see, the first thing tuttle does is to run the preprocesses to fully discover the workflow. Then it can
conclude that there is nothing to do because no process have changed.

We still need to add an html file into each photo directory, in order to displays the small photo and show the
download link :

    <html>
      <head>
        <title>Photo</title>
        <style>
            .photo {
              text-align: center;
              padding: 20px;
            }
        </style>
      </head>
      <body>
        <div class="photo">
            <h1>Photo</h1>
            <div> <img src="img_800x600.jpg"/> </div>
            <a href="img_download.jpg">Download</a>
        </div>
      </body>
    </html>

This file will be saved in our ``src`` directory as img_index.html. Then it will write in the ``src/img.tpl.tuttlefile``
that we want it copied in every image's directory. The new ``src/img.tpl.tuttlefile`` file with the thumbsnails, the
small image, the download link and the html file now looks like this :


    file://../web/{{img}} <- file://../images/{{img}}
    # creates the directory for the web page presenting the photo
        mkdir ../web/{{img}}

    file://../web/{{img}}/img_download.jpg <- file://../images/{{img}}, file://../web/{{img}}
    # add the avatar to the bottom left corner of the image and stores it to the web site
        composite -gravity SouthEast avatar100x100.jpg ../images/{{img}} ../web/{{img}}/img_download.jpg

    file://../web/{{img}} <- file://../images/{{img}}
    # creates the html index that will display the photo
        cp img_index.html ../web/{{img}}/index.html

    file://../web/{{img}}/img_frame.jpg <- file://../images/{{img}}, file://../web/{{img}}
    # create a a 800X600 image in the center of the html file
        convert {{img}} -resize 800x600 -bordercolor ../web/{{img}}/img_frame.jpg

    file://../web/thumbnails/{{img}} <- file://../images/{{img}}
    # create a a 200x150 thumbnail with border with imagemagick
        convert {{img}} -resize 200x150 -bordercolor white -border 20x20 ../web/thumbnails/{{img}}

Maybe you noticed a slight change in the file for download. Instead of keeping the original name, we name it
img_download.jpg, in order to have the same html index for every image. One again, when we run the workflow, tuttle
notices the previous files are not needed anymore and removes them :

    LOGS

Now we have the proper directory for every file in input !

What happens if we add a file in the ``image`` directory ? Tuttle knows it only have to process the new files :

    IMG

It could somehow seam strange to keep all the input images in the project, but it's a very robust way to know you
don't miss any. For example if you have some new photos every day, you could think of just running some code on the
new photos and then delete them. But if you miss one day BLA BLA BLA


It's interesting to notice that with this organisation, everything
EVERYTHING TO PROCESS FROM THE STATE

INDEX








For the moment we store this html template as img_index.html. Here is the overall structure of our project :
    src/                -> the tuttle source and utility files
        tuttlefile      -> the main project file
        img_index.html  -> the index.html for each image
        ...             -> some other files we'll need
    images/             -> the original input images
        IMG_001.jpg
        IMG_002.jpg
        ...
    web/                -> the directory where we want to create the web site described above
    
    
    
First, in the src directory, we'll create ``img.tpl.tuttlefile`` wich describes what do to with one image in the images directory :

    file://../web/thumbnails/{{img}} <- file://../images/{{img}}
    # create a a 200x150 thumbnail with border with imagemagick
        convert {{img}} -resize 200x150 -bordercolor white -border 20x20 ../web/thumbnails/{{img}}

    file://../web/{{img}} <- file://../images/{{img}}
    # creates the directory for the web page presenting the photo
        mkdir ../web/{{img}}

    file://../web/{{img}} <- file://../images/{{img}}
    # creates the html index that will display the photo
        cp img_index.html ../web/{{img}}/index.html

    file://../web/{{img}}/img.jpg <- file://../images/{{img}}, file://../web/{{img}}
    # store the downloadable original image in the directory
        cp ../images/{{img}} ../web/{{img}}/img.jpg
        
    file://../web/{{img}}/img_frame.jpg <- file://../images/{{img}}, file://../web/{{img}}
    # create a a 800X600 image in the center of the html file
        convert {{img}} -resize 800x600 -bordercolor ../web/{{img}}/img_frame.jpg    

As you can see, the {{img}} parameter represents the name of the image from the ``images/`` directory. The whole file uses the 
[jinja2](http://jinja.pocoo.org/) syntax to inject variables like ``img`` in the tuttlefile.

How to do that ?

The previous file is not a valid tuttlefile and can not be run as is. We'll have to add this snippet to the main tuttlefile 
for every photo in the ``images/`` directory. In order to do that, we'll run code *before* the workflow is run :
    
    |<<
        tuttle-extend-workflow img.tpl.tuttlefile img=IMG_001.jpg

The previous section, added to the main tuttlefile declares a *preprocess*. As the ``|<<`` suggests, it is run before any thing.
Therefore you can add some processes to the main workflow (with the tuttle-extend-workflow command), which injects the ``img`` variable
into the template we wrote.

Actually, we can create the needed part of the process for every image with a little of batch script :

    |<<
        for img_file in `ls images`
        do
           tuttle-extend-workflow img.tpl.tuttlefile img=$img_file
        done

If you're not familiar with the ``for`` syntax in shell, this code 




        
When crafting data from some other data, like packaging public data, using the good tools 
can really ease development process and reliability of the data. 

The venerable ``make`` which have already been used for decades to build software, is a very good option as advocated by Mike Bostock's in his [blog](https://bost.ocks.org/mike/make/). 

## A state-of-the-art Makefile

Let's take an example with crafting [geo-countries](http://github.com/datasets/geo-countries) datapackage. We need to download data from NaturalEarth, extract the zip, convert it to json with ogr (the ''swiss-army-knife'' of maps), and rename a column. Following Mike Bostok's instructions, here's an appropriate ``Makefile`` (that should lie the ``scripts`` folder of the project):

    all: ../data/countries.geojson
    
    ne_10m_admin_0_countries.zip:
    	wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip

    ne_10m_admin_0_countries.README.html ne_10m_admin_0_countries.VERSION.txt ne_10m_admin_0_countries.dbf ne_10m_admin_0_countries.prj ne_10m_admin_0_countries.shp ne_10m_admin_0_countries.shx: ne_10m_admin_0_countries.zip
    	unzip ne_10m_admin_0_countries.zip

    ne_10m_admin_0_countries.geojson: ne_10m_admin_0_countries.dbf ne_10m_admin_0_countries.prj ne_10m_admin_0_countries.shp ne_10m_admin_0_countries.shx
    	ogr2ogr -select admin,iso_a3  -f geojson ne_10m_admin_0_countries.geojson ne_10m_admin_0_countries.shp
        
    ../data:
    	mkdir ../data

    ../data/countries.geojson: ne_10m_admin_0_countries.geojson ../data
    # Change the name of the fields after conversion
    	cat ne_10m_admin_0_countries.geojson | sed 's/"admin": /"name": /g' | sed 's/"iso_a3": /"ISO3166-1-Alpha-3": /g'  > ../data/countries.geojson


If you're not familiar with Makefiles, the last section reads : "When both files ``ne_10m_admin_0_countries.geojson`` and ``../data`` are available, you can run command ``cat ne_10m_admin_0_countries.geojson | sed 's/"admin": /"name": /g' | sed 's/"iso_a3": /"ISO3166-1-Alpha-3": /g'  > ../data/countries.geojson``
and it will produce file ``../data/countries.geojson``". ``Make`` deduces the commands to be run, starting with the ones where everything is available, until it produces *target* ``all``.


We achieve two very important goals with this ``Makefile`` :
* it covers the whole process even the download part. It's so easy to forget wether we have downloaded ``ne_10m_admin_0_countries.zip`` or ``ne_110m_admin_0_countries.zip`` when it is done by hand. But now every thing is written down so we can keep track of it in our source repository (like git), even if we change our mind.
* Running ``make`` checks the date consistency of the files. That means that if Scottland has gone independent in 2015 it would have created a new country, that Natural Earth would have added. Now you can download the updated version of ``ne_10m_admin_0_countries.zip``. When running ``make`` again, it would notice that the unziped files like ``ne_10m_admin_0_countries.dbf`` and so on are older than their source, so the ``unzip`` command has to be run again ! And so on because ``ne_10m_admin_0_countries.geojson`` would not be up to date, until every depending file is updated.


Even if this is a great improvement over *running-all-the-commands-manually-and-don't-remember-them* as much *custom-script-that-must-start-from-scratch-every-time*, it is not enough to have a fluid and reliable development experience.

## Improve collaboration with ``tuttle``

Before we see in detail two major improvements, let's see the same workflow written in a ``tuttlefile`` (still in folder ``scripts``) :


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

It is very close to Makefile, except for urls everywhere. Because ``tuttle`` aims at giving a url to every bit of data, in order link them together.

You can see the first section of the tuttlefile clearly states the dependency of file ``ne_10m_admin_0_countries.zip`` to url ``http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip``. 
This means that when the online list of countries change, no unusual action is required. You just have to execute ``tuttle run`` as *if you where building the data for the first time*. It will notice the source url has changed and will reprocess dependencies accordingly.


The other difference with ``make`` is not in the syntax, it's in how it deals with changes in the ``tuttlefile``. If you ever worked with the ``ogr2ogr`` command line tool, you know it's impossible to make it right the first time. But if you change the command in a ``Makefile``, unfortunately running ``make`` again won't update the data because the date of the file ``ne_10m_admin_0_countries.geojson`` seem coherent.

To improve this, ``tuttle`` reacts to changes in every command. When you run it, it will first roll back as the previous command as if had never run by deleting whatever data has been produced. Then it will run the updated ogr2ogr command. That's very handy when prototyping because you want focus on your code without side effects caused by remaining data. 

This feature also proves really useful when working in a team. With ``make``, if you change the makefile, you need to send an mail to all your team with instructions of how to clean the workspace (ie : "Please remove file ../data/countries.geojson because I have changed the ogr2ogr command"), and hope nobody misses it because it would lead to undebuggable behaviour. On the other hand ``tuttle`` guaranties the data corresponds exactly the ``tuttlefile``, so you can safely share or merge changes with your fellow contributors.


## Conclusion

If you put both improvements over ``make`` together (remote dependencies and reliably reprocess what have changed), we can set up a system that automatically updates datapackages when either the original data changes or when someone modifies the source code. Pretty cool, huh ?

I hope I've convinced you of the advantages of tuttle for collectively crafting data. If you're interested, the best way to learn more about inline languages, url to databases or online resources, is to read the [main tutorial](https://github.com/lexman/tuttle/master/doc/tuttorial).


And one more thing about the sugar syntax you can expect... You could simplify the first section of the ``tuttlefile`` in only one line :

    file://ne_10m_admin_0_countries.zip <- http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip ! download
