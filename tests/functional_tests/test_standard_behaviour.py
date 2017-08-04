# -*- coding: utf-8 -*-
from os.path import isfile, exists, isdir

from os import path
from tests.functional_tests import isolate, run_tuttle_file
from tuttle.tuttle_directories import TuttleDirectories


class TestStandardBehaviour:

    @isolate(['A'])
    def test_create_resource(self):
        """ When launching "tuttle" in the command line, should produce the result"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

"""
        rcode, output = run_tuttle_file(first)
        assert path.exists('B')

    @isolate(['A'])
    def test_create_report(self):
        """ When launching "tuttle" in the command line, should produce the result"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

"""
        rcode, output = run_tuttle_file(first)
        assert path.exists(path.join('.tuttle', 'report.html'))

    @isolate(['A'])
    def test_report_execution(self):
        """ When launching "tuttle" in the command line, should produce the html report"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    error
    echo B produces C
    echo C > C

file://D <- file://C
    echo C produces D
    echo D > D
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 2, output
        assert isfile(path.join(".tuttle", 'report.html'))
        assert path.isfile(path.join(".tuttle", "last_workflow.pickle"))
        second = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    another error
    echo B produces C
    echo C > C

file://D <- file://C
    echo C produces D
    error
    echo D > D
"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 2
        report = file(path.join('.tuttle', 'report.html')).read()
        [_, sec1, sec2, sec3] = report.split('<h2')
        assert sec1.find("<th>Start</th>") >= 0, sec1
        assert sec2.find("<th>Start</th>") >= 0, sec2
        assert sec3.find("<th>Start</th>") == -1, sec3

    @isolate(['A'])
    def test_workflow_execution_should_stop_at_first_process_error(self):
        """ Should invalidate a resource if the code creating it changes
        """
        project = """file://B <- file://A
        echo A produces B > B
        error

file://C <- file://B
        echo B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        assert not path.exists('C')

    @isolate(['A'])
    def test_should_tell_if_already_ok(self):
        """ If nothing has to run, the user should be informed every thing is ok
        """
        project = """file://B <- file://A
        echo A produces B > B
        echo A produces B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("A produces B") >= 0, output
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("Nothing to do") >= 0, output

    @isolate(['A', 'tuttlefile'])
    def test_tuttlefile_should_be_in_utf8(self):
        """ If nothing has to run, the user should be informed every thing is ok
        """
        rcode, output = run_tuttle_file()
        assert rcode == 0, output
        result = file('B').read().decode('utf8')
        assert result.find(u"du texte accentué") >= 0, result

    @isolate(['A'])
    def test_processes_paths(self):
        """ After a process has run, former logs and reserved_path should have moved according to
            the new name of the process
        """
        project = """file://B <- file://A
        echo A produces B > B
        echo A has produced B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

        out_log = open(TuttleDirectories.tuttle_dir("processes", "logs", "tuttlefile_1_stdout.txt")).read()
        assert out_log.find("A has produced B") > -1, out_log

        assert exists(TuttleDirectories.tuttle_dir("processes", "tuttlefile_1"))
        # out_log = open(TuttleDirectories.tuttle_dir("processes", "tuttlefile_1")).read()
        # assert out_log.find("echo A has produced B") > -1, out_log

        project = """file://C <- file://A ! python
    f = open('C', 'w')
    f.write('A produces C')
    print('echo A has produced C')

file://B <- file://A
        echo A produces B > B
        echo A has produced B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

        out_log = open(TuttleDirectories.tuttle_dir("processes", "logs", "tuttlefile_6_stdout.txt")).read()
        assert out_log.find("A has produced B") > -1, out_log

        reserved_path = TuttleDirectories.tuttle_dir("processes", "tuttlefile_6")
        if isdir(reserved_path):
            script = TuttleDirectories.tuttle_dir("processes", "tuttlefile_6", "tuttlefile_6.bat")
        else:
            script = reserved_path
        out_log = open(script).read()
        assert out_log.find("echo A has produced B") > -1, out_log

    @isolate(['A'])
    def test_preprocesses_paths(self):
        """ After a workflow has run, logs and reserved path from preprocesses should be available (from bug)
        """
        project = """file://B <- file://A
    echo A produces B > B
    echo A has produced B
        
|<<
    echo Preprocess running
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

        out_log = open(TuttleDirectories.tuttle_dir("processes", "logs", "tuttlefile_5_stdout.txt")).read()
        assert out_log.find("Preprocess running") > -1, out_log
        assert exists(TuttleDirectories.tuttle_dir("processes", "tuttlefile_5"))
