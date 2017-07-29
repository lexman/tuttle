# -*- coding: utf8 -*-
import os


class CurrentDir(object):
    """
    Step into a directory temporarily.
    """
    def __init__(self, path):
        self.old_dir = os.getcwd()
        self.new_dir = path
 
    def __enter__(self):
        os.chdir(self.new_dir)
 
    def __exit__(self, *args):
        os.chdir(self.old_dir)


class EnvVar(object):
    """
    Adds an environment variable temporarily.
    """
    def __init__(self, var, value):
        self.var = var
        self.value = value

    def __enter__(self):
        if os.environ.has_key(self.var):
            self.former_value = os.environ[self.var]
        else:
            self.former_value = None
        os.environ[self.var] = self.value

    def __exit__(self, *args):
        if self.former_value is not None:
            os.environ[self.var] = self.former_value
        else:
            del os.environ[self.var]
