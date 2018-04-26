# -*- coding: utf-8 -*-
import os
from subprocess import Popen, PIPE
from time import sleep

import signal
from nose.plugins.skip import SkipTest

from tests.functional_tests import isolate
from tuttle.workflow import Workflow


class TestKeyboardInterrupt:

    def setUp(self):
        if os.name != 'posix':
            raise SkipTest("Testing keyboard interrupt only works on *nix")

    @isolate(['A'])
    def test_interrupt_exit_code(self):
        """ Should exit with code code when interrupted """
        project = """file://B <- file://A
    echo A produces B
    sleep 1
    echo B > B

"""
        with open('tuttlefile', "w") as f:
            f.write(project)
        proc = Popen(['tuttle', 'run'], stdout=PIPE)

        sleep(0.5)
        proc.send_signal(signal.SIGINT)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2, output
        # assert output.find("Process tuttlefile_1 aborted by user") > -1, output
        assert output.find("Interrupted") > -1, output
        w = Workflow.load()
        pB = w.find_process_that_creates("file://B")
        assert pB.end is not None, "Process that creates B should have ended"
        assert pB.success is False, "Process that creates B should have ended in error"
        assert pB.error_message.find("aborted") >= -1, "Process that creates B should be declared as aborted"

    @isolate(['A'])
    def test_relaunch_after_interrupt(self):
        """ Tuttle should run again after it has been interrupted"""
        project = """file://B <- file://A
    sleep 1
    echo B > B
"""
        with open('tuttlefile', "w") as f:
            f.write(project)
        proc = Popen(['tuttle', 'run'], stdout=PIPE)

        sleep(0.5)
        proc.send_signal(signal.SIGINT)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2, output

        proc = Popen(['tuttle', 'run'], stdout=PIPE, stderr=PIPE)
        rcode = proc.wait()
        err = proc.stderr.read()
        output = proc.stdout.read()
        assert rcode == 2, output
        assert output.find("already failed") > -1, output + "\n" + err

    @isolate(['A'])
    def test_relaunch_after_kill(self):
        """ Tuttle should run again after it has been killed (from bug)"""
        # raise SkipTest()
        project = """file://B <- file://A
    echo B > B
    sleep 1
"""
        with open('tuttlefile', "w") as f:
            f.write(project)
        proc = Popen(['tuttle', 'run'], stdout=PIPE)

        sleep(0.5)
        proc.send_signal(signal.SIGKILL)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == -signal.SIGKILL, output

        proc = Popen(['tuttle', 'run'], stdout=PIPE, stderr=PIPE)
        rcode = proc.wait()
        err = proc.stderr.read()
        assert err.find("DISCOVERED") < 0, err
