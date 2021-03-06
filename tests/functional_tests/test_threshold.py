# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
from os.path import isfile
from tests.functional_tests import isolate, run_tuttle_file


class TestThreshold:

    @isolate(['A'])
    def test_abort_if_lost_exceeds_threshold(self):
        """ Should disply a message and abort if processing time lost by invalidation is above the threshold """
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    echo B produces C
    python -c "import time; time.sleep(1.3)"
    echo C > C
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert isfile('C')
        second = """file://B <- file://A
    echo B has changed
    echo B has changed > B

file://C <- file://B
    echo B produces C
    python -c "import time; time.sleep(1.3)"
    echo C > C
"""
        rcode, output = run_tuttle_file(second, threshold=1)
        assert rcode == 2, output
        assert output.find("Aborting") >= 0, output

    @isolate(['A'])
    def test_not_abort_if_lost_not_exceeds_threshold(self):
        """ Should disply a message and abort if processing time lost by invalidation is above the threshold """
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    echo B produces C
    echo C > C
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert isfile('C')
        second = """file://B <- file://A
    echo B has changed
    echo B has changed > B

file://C <- file://B
    echo B produces C
    echo C > C
"""
        rcode, output = run_tuttle_file(second, threshold=1)
        assert rcode == 0, output
        assert output.find("Aborting") == -1, output

    @isolate(['A'])
    def test_not_abort_if_threshold_is_0(self):
        """ Should abort if threshold whatever lost time is"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    echo B produces C
    echo C > C
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert isfile('B')
        assert isfile('C')

        second = """file://B <- file://A
    echo B has changed
    echo B has changed > B

file://C <- file://B
    echo B produces C
    echo C > C
"""
        rcode, output = run_tuttle_file(second, threshold=0)
        assert rcode == 2, output
        assert output.find("Aborting") >= 0, output
        assert isfile('B')
        assert isfile('C')

    @isolate(['A'])
    def test_threshold_in_command_line_run(self):
        """ The threshold -t parameter should be available from the command line"""
        first = """file://B <- file://A
    echo A produces B
    python -c "import time; time.sleep(1)"
    echo B > B

file://C <- file://B
    echo B produces C
    echo C > C
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert isfile('B')

        second = """file://B <- file://A
    echo B has changed
    echo B has changed > B
"""
        with open('tuttlefile', "w") as f:
            f.write(second)
        proc = Popen(['tuttle', 'run', '-t', '1'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2, output

        assert output.find('Aborting') >= 0, output
        assert isfile('B'), output

    @isolate(['A'])
    def test_duration_threshold_in_command_line_run(self):
        """ The threshold -t parameter could be a duration string eg 3h2min """

        project = """file://B <- file://A
    echo A produces B > B
"""
        with open('tuttlefile', "w") as f:
            f.write(project)
        proc = Popen(['tuttle', 'run', '-t', '3min2s'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 0, output

    @isolate(['A'])
    def test_bad_duration_threshold_error(self):
        """ If the threshold -t parameter has a bad value, tuttle should display an error """

        project = """file://B <- file://A
    echo A produces B > B
"""
        with open('tuttlefile', "w") as f:
            f.write(project)
        proc = Popen(['tuttle', 'run', '-t', '3min2s4ms'], stdout=PIPE, stderr=PIPE)
        errormsg = proc.stderr.read()
        rcode = proc.wait()
        assert rcode == 2, errormsg
        assert errormsg.find('valid duration') >= 0, errormsg


    @isolate(['A'])
    def test_negative_threshold_in_command_line_run(self):
        """ The threshold -t parameter can't be negative """

        project = """file://B <- file://A
    echo A produces B > B
"""
        with open('tuttlefile', "w") as f:
            f.write(project)
        proc = Popen(['tuttle', 'run', '-t', '-2'], stdout=PIPE, stderr=PIPE)
        errormsg = proc.stderr.read()
        rcode = proc.wait()
        assert rcode == 2, errormsg
        assert errormsg.find('negative') >= 0, errormsg

    @isolate(['A'])
    def test_ignore_default_threshold(self):
        """ Threshold should be ignored if not provided or left to default value"""
        first = """file://B <- file://A
    echo A produces B
    python -c "import time; time.sleep(1.3)"
    echo B > B
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert isfile('B')

        second = """file://B <- file://A
    echo B has changed
    echo B has changed > B
"""
        with open('tuttefile', "w") as f:
            f.write(second)

        proc = Popen(['tuttle', 'run'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 0, output
        assert output.find('Aborting') == -1, output

    @isolate(['A'])
    def test_threshold_in_command_line_invalidate(self):
        """ The threshold -t parameter should be available from the invalidate command"""
        first = """file://B <- file://A
    echo A produces B
    python -c "import time; time.sleep(1.3)"
    echo B > B
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert isfile('B')

        proc = Popen(['tuttle', 'invalidate', '-t', '1', 'file://B'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2, output

        assert output.find('Aborting') >= 0, output
        assert isfile('B'), output

    @isolate(['A'])
    def test_threshold_with_outputless_processes(self):
        """ The threshold should take into account outputless processes (from bug) """
        project = """file://B <- file://A
    echo A produces B
    echo A produces B > B

 <- file://B 
    python -c "import time; time.sleep(1.1)"
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert isfile('B')

        proc = Popen(['tuttle', 'invalidate', '-t', '1', 'file://B'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2, output

        assert output.find('Aborting') >= 0, output
        assert isfile('B'), output
