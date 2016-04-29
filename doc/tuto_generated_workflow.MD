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

The last two lines in the main tuttlefile declares a *preprocess*. As the symbol ``|<<`` suggests (it is supposed to
look like a rewind button), this code will be executed *before* the whole workflow is run.

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

