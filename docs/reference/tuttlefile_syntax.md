# Tuttlefile Syntax

A tuttlefile is made with several sections wich can be one of the following.

## Processes
The main elements of a tuttlefile file are ``processes``

Each process describe how to get ``output resources`` from ``input resources`` with some ``code``. A block of ``code``
is identified because every line start with the same indentation. Code is interpreted by tuttle
according to the ``processor`` chosen for the process.

For example a process producing two outputs from three inputs according to my_processor can look like that

```
scheme://output/resource/1 scheme://output/resource/2 <- scheme://input/resource/1 scheme://input/resource/2 scheme://input/resource/3 ! my_processor
    first line of code
    second line of code
```

Input and output resources are both space separated lists of urls. An arrow ``<-`` separate inputs from outputs, and empty lists on either side
are valid.

Then comes an optional exclamation mark ``!`` with the processor name. By default, ``processor`` is ``shell`` under Linux
(and ``batch`` under windows)

Input, outputs and processor must all be on the same line (for the moment).

## Includes
Also, tuttle projects can be split in several files with the ``include`` statement :

```
include another_tuttlefile.tuttle
```

## Preprocesses
If the usual syntax is not powerfull enought to let you describe your workflow, maybe because there is yesterdays date in the name in input files, or
you must apply the same processing to a list of images in a directory, you can use *preprocesses* to add parts to your workflow with code.

All preproceses are run early, even before tuttle checks that the workflow is valid. The shouldn't have side effects (like creating files) because
tuttle can't clean after a preprocess has run.

Proceprocesses look like :

    |<< ! shell
        tuttle-extend-workflow img.tpl.tuttlefile img=IMG_001.jpg

Preprocesses are an advanced feature of tuttle you can learn on, the [parametrized workflow tutorial](tuto_parametrized_workflow/tuto_parametrized_workflow.MD).
