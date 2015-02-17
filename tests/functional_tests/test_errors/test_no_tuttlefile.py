# -*- coding: utf-8 -*-

from subprocess import check_output
from tests.functional_tests import FunctionalTestBase

class TestNoTuttlefile(FunctionalTestBase):

    def test_no_file_in_current_dir(self):
        """ Should display a message if there is no tuttlefile in the current directory"""
        self.work_dir_from_module(__file__)
        result = self.run_tuttle()
        assert result.find("No tuttlefile") >= 0


    def test_tuttle_file_does_not_exist(self):
        """ Should display a message if the tuttlefile passed as argument to the command line does not exist"""
        result = check_output(['python', self._tuttle_cmd, '-f', 'inexistant_file'], shell=True)
        assert result.find("No tuttlefile") >= 0
