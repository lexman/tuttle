# -*- coding: utf-8 -*-
from tempfile import mkdtemp

import sys
from os import getcwd, chdir
from shutil import rmtree, copy
from functools import wraps
from os.path import join, dirname
from cStringIO import StringIO
from tuttle.commands import parse_invalidate_and_run


def run_tuttle_file(content=None, threshold=-1, nb_workers=-1):
    if content is not None:
        with open('tuttlefile', "w") as f:
            f.write(content.encode("utf8"))
    oldout, olderr = sys.stdout, sys.stderr
    out = StringIO()
    try:
        sys.stdout,sys.stderr = out, out
        rcode = parse_invalidate_and_run('tuttlefile', threshold=threshold, nb_workers=nb_workers)
    finally:
        sys.stdout, sys.stderr = oldout, olderr
    return rcode, out.getvalue()


def isolate(arg):
    if isinstance(arg, list):
        files = arg
    elif callable(arg):
        files = []

    def wrap(func):
        funct_dir = dirname(func.func_globals['__file__'])

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            tmp_dir = mkdtemp()
            for filename in files:
                src = join(funct_dir, filename)
                dst = join(tmp_dir, filename)
                copy(src, dst)
            cwd = getcwd()
            chdir(tmp_dir)
            try:
                return func(*args, **kwargs)
            finally:
                chdir(cwd)
                rmtree(tmp_dir)
        return wrapped_func
    if isinstance(arg, list):
        return wrap
    elif callable(arg):
        return wrap(arg)
