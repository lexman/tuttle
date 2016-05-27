# Parametrized workflows

This tutorial assumes you are already familiar with ``tuttle`` and you already understand the [main tutorial](tutorial_musketeers/tutorial.md). But you've been stuck in a use case : you 
don't know all your inputs... It could be either because you want to process all the files form a directory, or because your workflow depends on a 
configuration file you can only get with custom code in your favourite language.

We'll use the first case a an example. Let's assume we want to publish a list of images to the web, and we want to resize them
with [imgagemagick](http://www.imagemagick.org/), add my github avatar from to mark property, and allow the user to download
the photo with the original size.

# Organize the project

First, the way to get the avatar and resize it to 100x100 is very classic. Here's our ``tuttlefile`` :

    file://avatar.jpg <- https://avatars.githubusercontent.com/u/2512784 ! download

    file://avatar200x200.jpg <- file://avatar.jpg
    # Use imagemagick to resize the avatar
        convert avatar.jpg -resize 200x200 avatar200x200.jpg

We can store it on the ``src`` directory of our project. Then we can run tuttle in the src directory and see everything works fine :

    cd src
    tuttle run

You should see ![me](https://avatars.githubusercontent.com/u/2512784) in your project directory :)


Now that's done, let's have a look at the overall structure of the sources our project :
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

# Expected output

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

Before any else, we need to add those lines to the `tuttlefile` to create the necessary directories to welcome this structure :

    file://../web, file://../web/thumbnails <- 
        mkdir ../web
        mkdir ../web/thumbnails    
        
        
# Design a workflow with parameter
        
For every picture in the ``images`` path, we need to create a subdirectory in the web directory and create the
download image. My small avatar should appear on the bottom left corner of the image. In order to do that, we'll
create a ``src/img.tpl.tuttlefile`` file that will have all the tuttle code for one image :


    file://../web/{{img}} <- file://../images/{{img}}, file://../web
    # creates the directory for the web page presenting the picture
        mkdir ../web/{{img}}

    file://../web/{{img}}/{{img}} <- file://../images/{{img}}, file://../web/{{img}}, file://avatar200x200.jpg
    # add the avatar to the bottom left corner of the image and stores it to the web site
        echo "Adding the avatar on picture {{img}}"
        composite -gravity SouthWest avatar200x200.jpg ../images/{{img}} ../web/{{img}}/{{img}}

As you can see, the {{img}} parameter represents the name of the image from the ``images/`` directory. The whole
file uses the [jinja2](http://jinja.pocoo.org/) syntax to inject variables like ``img`` in the tuttlefile.


# How to inject the variable for each image ? Preprocess !

The previous file is not a valid tuttlefile and can not be run as is. We have to add two lines in the end of the
tuttlefile in order to apply the previous snippet to the first file in our image directory : IMG_001.jpg

    file://avatar.jpg <- https://avatars.githubusercontent.com/u/2512784 ! download

    file://avatar200x200.jpg <- file://avatar.jpg
    # Use imagemagick to resize the avatar
        convert avatar.jpg -resize 200x200 avatar200x200.jpg

    file://../web, file://../web/thumbnails <- 
        mkdir ../web
        mkdir ../web/thumbnails    
        
    |<<
        tuttle-extend-workflow img.tpl.tuttlefile img=IMG_001.jpg

The last two lines in the main tuttlefile declares a *preprocess*. As the symbol ``|<<`` suggests (it is supposed to
look like a rewind button), this code will be executed *before* the whole workflow is run.

Therefore you can add some extra processes to the main workflow (with the tuttle-extend-workflow command), which
injects the ``img`` variable into the template we wrote.

Actually, anyone familiar with the ``for`` syntax in shell can create new part of the workflow for
every image :

    |<<
        IMAGES=`ls ../images`
        for IMG in $IMAGES
        do
           echo "Tuttle will work on ../images/$IMG"
           tuttle-extend-workflow img.tpl.tuttlefile img=$IMG
        done

Let's ``tuttle run`` this workflow. 

    ============================================================
    Running preprocesses for this workflow
    ============================================================
    ------------------------------------------------------------
    Preprocess : tuttlefile_7
    ------------------------------------------------------------
    --- stdout : -----------------------------------------------
    Tuttle will work on FILE0016.JPG
    Tuttle will work on FILE0070.JPG
    Tuttle will work on P1090294.JPG

    ============================================================
    End of preprocesses... Running the workflow
    ============================================================
    ============================================================
    extension1_1
    ============================================================
    ============================================================
    extension1_5
    ============================================================
    --- stdout : -----------------------------------------------
    Adding the avatar on picture FILE0016.JPG

    ============================================================
    extension2_1
    ============================================================
    ============================================================
    extension2_5
    ============================================================
    --- stdout : -----------------------------------------------
    Adding the avatar on picture FILE0070.JPG

    ============================================================
    extension3_1
    ============================================================
    ============================================================
    extension3_5
    ============================================================
    --- stdout : -----------------------------------------------
    Adding the avatar on picture P1090294.JPG

    ====
    Done

As expected, tuttle has two processes for eahc images. We can see the dependency graph show the new processes :

![Dependency graph of parametrized workflow](dep_graph_3_imgs.png)

We can see that for every picture in the ``images`` directory (``FILE0016.JPG``, ``FILE0070.JPG``, ``P1090294.JPG``), tuttle has created the expected image with my avatar on it.


Note that all the preprocesses are run once and for all before trying to run the workflow. This means tuttle can
still make some *static* analysis on the workflow to detect missing resources, wrong definitions or circular
references. All the processes are known at that time.

For example let's ``tuttle run`` again :

    ============================================================
    Running preprocesses for this workflow
    ============================================================
    ------------------------------------------------------------
    Preprocess : tuttlefile_7
    ------------------------------------------------------------
    --- stdout : -----------------------------------------------
    Tuttle will work on FILE0016.JPG
    Tuttle will work on FILE0070.JPG
    Tuttle will work on P1090294.JPG

    ============================================================
    End of preprocesses... Running the workflow
    ============================================================
    Nothing to do

As we can see, the first thing tuttle does is to run the preprocesses to fully discover the workflow. Then it can
conclude that there is nothing to do because no process have changed.

# Apply these principles to generate the rest of the site

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
that we want it copied in every image's directory. The new ``src/img.tpl.tuttlefile`` file with the thumbnails, the
small image, the download link and the html file now looks like this :


    file://../web/{{img}} <- file://../images/{{img}}, file://../web
    # creates the directory for the web page presenting the picture
        mkdir ../web/{{img}}

    file://../web/{{img}}/img_download.jpg <- file://../images/{{img}}, file://../web/{{img}}, file://avatar200x200.jpg
    # add the avatar to the bottom left corner of the image and stores it to the web site
        echo "Adding the avatar on picture {{img}}"
        composite -gravity SouthWest avatar200x200.jpg ../images/{{img}} ../web/{{img}}/img_download.jpg

    file://../web/{{img}}/index.html <- file://img_index.html, file://../web/{{img}}
    # creates the html index that will display the picture
        cp img_index.html ../web/{{img}}/index.html

    file://../web/{{img}}/img_800x600.jpg <- file://../images/{{img}}, file://../web/{{img}}
    # create a a 800X600 image in the center of the html file
        convert ../images/{{img}} -resize 800x600 ../web/{{img}}/img_800x600.jpg

    file://../web/thumbnails/{{img}} <- file://../images/{{img}}, file://../web/thumbnails
    # create a a 200x150 thumbnail with border with imagemagick
        convert ../images/{{img}} -resize 200x150 -bordercolor white -border 20x20 ../web/thumbnails/{{img}}

Maybe you noticed a slight change in the file for download. Instead of keeping the original name, we name it
img_download.jpg, in order to have the same html index for every image. One again, when we run the workflow, tuttle
notices the previous files are not needed any more and removes them :

    ============================================================
    Running preprocesses for this workflow
    ============================================================
    ------------------------------------------------------------
    Preprocess : tuttlefile_11
    ------------------------------------------------------------
    --- stdout : -----------------------------------------------
    Tuttle will work on FILE0016.JPG
    Tuttle will work on FILE0070.JPG
    Tuttle will work on P1090294.JPG

    ============================================================
    End of preprocesses... Running the workflow
    ============================================================
    The following resources are not valid any more and will be removed :
    * file://../web/P1090294.JPG/P1090294.JPG - Resource no longer created by the newer process
    * file://../web/FILE0016.JPG/FILE0016.JPG - Resource no longer created by the newer process
    * file://../web/FILE0070.JPG/FILE0070.JPG - Resource no longer created by the newer process
    5 seconds of processing will be lost
    ============================================================
    extension1_5
    ============================================================
    --- stdout : -----------------------------------------------
    Adding the avatar on picture FILE0016.JPG

    ============================================================
    extension1_10
    ============================================================
    ============================================================
    extension1_14
    ============================================================
    ============================================================
    extension1_18
    ============================================================
    ============================================================
    extension2_5
    ============================================================
    --- stdout : -----------------------------------------------
    Adding the avatar on picture FILE0070.JPG

    ============================================================
    extension2_10
    ============================================================
    ============================================================
    extension2_14
    ============================================================
    ============================================================
    extension2_18
    ============================================================
    ============================================================
    extension3_5
    ============================================================
    --- stdout : -----------------------------------------------
    Adding the avatar on picture P1090294.JPG

    ============================================================
    extension3_10
    ============================================================
    ============================================================
    extension3_14
    ============================================================
    ============================================================
    extension3_18
    ============================================================
    ====
    Done

Now we have the proper directory for every file in input !

What happens if we add a file in the ``image`` directory ? Tuttle knows it only have to process the new files :

![The new picture has to be processes](new_img.png)

It could somehow seam strange to keep all the input images in the project, but it's a very robust design. And you can 
easily un-publish a photo :)


# Generate the index

The last part of the site is the index of the photos. We can generate it with a little of python code... And this 
html template ``index.tpl.html`` :

    <html>
      <head>
        <title>My holiday pictures</title>
      </head>
      <body>
          <h1 style="text-align: center">My holiday pictures</h1>
          <div>
          {% for img in images %}
                <a href="{{img}}/index.html"> <img src="thumbnails/{{img}}"/> </a>
          {% endfor %}
          </div>
      </body>
    </html>

This is the same template language as we've used before, but it has nothing to do with tuttle. It's just a very common language
on the web. Here, we use a ``for`` structure in the template, to repeat the inner html structure for each image. Here's the 
python code to create the index :
    
    from jinja2 import Template
    from os.path import join
    from os import listdir
    TPL = 'index.tpl.html'
    INDEX = join('..', 'web', 'index.html')
    THUMBS = join('..', 'web', 'thumbnails')

    with open(TPL, 'rb') as ftpl:
        t = Template(ftpl.read().decode('utf8'))

    thumbfiles = listdir(THUMBS)

    with open(INDEX, 'wb') as fout:
        content = t.render(images=thumbfiles)
        fout.write(content.encode('utf8)'))
    
In this code we've read a the html templa file to create a template variable ``t``. Then we read the list of thumbnails, 
and we inject the list of thumbnails in our variable ``images`` that will be used by the previous ``for`` structure.

How do we insert this code in our project ? 

All the thumbnails must have been created for this code to run properly, so we'll write a rule stating that the index 
depends on all the thumbnail. Once again we'll need a template tuttlefile, and we'll use the new jinja2 ``for`` structure 
we have learned. Hence, the ``index.tpl.tuttlefile`` looks like :

    file://../web/index.html <- file://index.tpl.html, {% for img in images %} file://../web/thumbnails/{{img}} {% if not loop.last %},{%endif%} {% endfor %} ! python
        from jinja2 import Template
        from os.path import join
        from os import listdir
        TPL = 'index.tpl.html'
        INDEX = join('..', 'web', 'index.html')
        THUMBS = join('..', 'web', 'thumbnails')

        with open(TPL, 'rb') as ftpl:
            t = Template(ftpl.read().decode('utf8'))

        thumbfiles = listdir(THUMBS)

        with open(INDEX, 'wb') as fout:
            content = t.render(images=thumbfiles)
            fout.write(content.encode('utf8)'))
    
And we can include this extension in our main tuttlefile, either in the same preprocess or in a new one (yes, you can have
several preprocess) : 

    |<<
        IMAGES=`ls ../images`
        tuttle-extend-workflow index.tpl.tuttlefile images[]=$IMAGES

The brackets in ``images[]`` specify that the ``image`` variable is an array, and that value will
be on the command line separated by spaces. That's how we set the list of images to iterate in the template file.

# Extend from python

In case your inputs are as simple as all the files from a directory, or if you want a portable project executable either under windows or Linux, you can switch 
you preprocess to python :

    |<< !python
        from tuttle import extend_workflow
        from os import listdir
        from os.path import join
        images = listdir(join('..', 'images')
        extend_workflow('index.tpl.tuttlefile', images=images)

In python you can use the ``extend_workflow`` function to add some extra processes.
        

# Conclusion
You can use these parametrized sub-workflows when you don't know the list of input resources at the time you write the tuttlefile. It can be a list of pictures inside a directory 
you need to put online, a configuration file that states a list of urls to archive, or the graphic assets of an application that you have to resize for every phone's resolutions.
Usualy you'll add extra processes from a shell (or a batch, under windows) preprocess, but if you want more control you can use any language implemented in tuttle, 
if it offers an API to do it. At the moment, this means Python...

