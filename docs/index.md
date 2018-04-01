# Overview


The best way to discover tuttle is the [main tutorial](tutorial_musketeers/tutorial.md) : counting the importance of each musketeer in the novel
'The Three Musketeers' : python + awk + gnuplot. It explains in deep details how to use tuttle to work smoothly.

If you're familiar with `make`, the article [Make vs tuttle](http://okfnlabs.org/blog/2016/03/25/make-vs-tuttle.html) on OKFN labs is also a good introduction.

Once your familiar with tuttle's workflow, you can find the details of processors and url schemes in the
[tuttlefile reference](reference/tuttlefile_reference.md)

Some tuttle projects of interest :
* https://github.com/datasets/world-cities/blob/master/scripts/tuttlefile : example of ``sqlite://`` resources and ``sqlite`` processor
* https://github.com/lexman/carte-de-mon-departement : example of parametrized workflow

If you're stuck because you don't know all your inputs at the time of writing your tuttlefile, for exemple because you want to process all the files 
from a directory, you can learn how to use [parametrized workflows](tuto_parametrized_workflow/tuto_parametrized_workflow.MD).