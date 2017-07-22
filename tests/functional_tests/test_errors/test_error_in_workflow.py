# -*- coding: utf-8 -*-

from tests.functional_tests import isolate, run_tuttle_file


class TestErrorInWorkflow():

    @isolate
    def test_missing_primary_resource(self):
        """ Should fail if a primary resource is missing"""
        project = """file://B <- file://A
    echo A produces B
    echo B > B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 2, rcode
        assert output.find("Missing") >= 0, output

    @isolate
    def test_circular_references(self):
        """ Should fail if a primary resource is missing"""
        project = """file://B <- file://A
file://A <- file://B
    echo A produces B
    echo B > B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 2, rcode
        assert output.find("circular") >= 0, output

    @isolate
    def test_ambiguous_outputless_processes(self):
        """ Should not allow two outputless processes with same inputs"""
        project = """ <- file://A
    echo Do something with file A
        
 <- file://A
    echo Do something else with file A
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 2, rcode
        assert output.find("both have exactly the same inputs") >= 0, output
