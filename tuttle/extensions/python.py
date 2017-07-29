# -*- coding: utf8 -*-

from os import path, chmod, stat, mkdir
from stat import S_IXUSR, S_IXGRP, S_IXOTH
from subprocess import Popen, PIPE
from tuttle.error import TuttleError
from tuttle.processors import run_and_log



class PythonProcessor:
    """ A processor to run python2 code
    """
    name = 'python'
    header = u"""# -*- coding: utf8 -*-
from os import getcwd as __get_current_dir__
from sys import path as __python__path__
__python__path__.append(__get_current_dir__())
"""

    def generate_executable(self, process, reserved_path):
        """ Create an executable file
        :param directory: string
        :return: the path to the file
        """
        mkdir(reserved_path)
        script_name = path.abspath(path.join(reserved_path, "{}.py".format(process.id)))
        with open(script_name, "w+") as f:
            f.write(self.header.encode("utf8"))
            f.write(process._code.encode('utf8'))
        return script_name

    def run(self, process, reserved_path, log_stdout, log_stderr):
        script = self.generate_executable(process, reserved_path)
        run_and_log(["python", script], log_stdout, log_stderr)

    def static_check(self, process):
        pass

