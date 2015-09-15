# tuttlefilet reference

## syntax
A tuttlefile is made of several ''processes''

Each process describe how to get ``output resources`` from ``input resources`` with some ``code``. A block of ``code``
is identified because every line start with the same indentation. Code can be interpreted
according to the ``processor`` chosen for the process.

For example a process producing two outputs from three inputs according to my_processor can look like that

```
schema:\\output\resource\1, schema:\\output\resource2 <- schema:\\input\resource1, schema:\\input\resource2, schema:\\input\resource3 ! my_processor
    first line of code
    second line of code
```

Input and output resources are both coma separated lists of urls. An arrow ``<-`` make the separation, and empty lists
are valid.

Then comes an optional exclamation mark ``!`` with the processor name. By default, ``processor`` is ``shell`` under Linux
(and ``batch`` under windows)

Input, outputs and processor must all be on the same line (for the moment).


