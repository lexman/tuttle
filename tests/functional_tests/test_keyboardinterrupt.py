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


