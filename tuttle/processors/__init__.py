#!/usr/bin/env python
# -*- coding: utf8 -*-

from os import path, chmod, makedirs, stat
from stat import S_IXUSR, S_IXGRP, S_IXOTH
from subprocess import Popen, PIPE

class ShellProcessor:
    """ A processor runs process code
    """
    name = 'shell'


    header = """
echo "Shell process"
"""


    def __init__(self):
        pass

    def generate_executable(self, code, line_num, directory):
        """ Create an executable file
        :param directory: string
        :return: the path of the file
        """
        script_name = path.join(directory, "shell_{}.bat".format(line_num))
        with open(script_name, "w+") as f:
            f.write(self.header)
            f.write(code)
        mode = stat(script_name).st_mode
        chmod(script_name, mode | S_IXUSR | S_IXGRP | S_IXOTH)
        return script_name

    def run(self, script_path):
        log_dir = path.join(path.dirname(script_path), 'logs')
        if not path.isdir(log_dir):
            makedirs(log_dir)
        osprocess = Popen([path.abspath(script_path)], stdout=PIPE, stderr=PIPE)
        stdout, stderr = osprocess.communicate()
        print stdout
        script_name = path.basename(script_path)
        with open(path.join(log_dir, "{}_stdout".format(script_name)), 'w') as f:
            f.write(stdout)
        with open(path.join(log_dir, "{}_err".format(script_name)), 'w') as f:
            f.write(stderr)
