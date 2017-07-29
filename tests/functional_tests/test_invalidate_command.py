# -*- coding: utf-8 -*-

import sys
from subprocess import Popen, PIPE
from os.path import join, isfile
from re import search, DOTALL
from tests.functional_tests import isolate, run_tuttle_file
from cStringIO import StringIO
from tuttle.commands import invalidate_resources
from tuttle.invalidation import BROTHER_INVALID


class TestCommands:

    def tuttle_invalide(self, project=None, urls=[]):
        if project is not None:
            with open('tuttlefile', "w") as f:
                f.write(project)
        oldout, olderr = sys.stdout, sys.stderr
        out = StringIO()
        try:
            sys.stdout, sys.stderr = out, out
            rcode = invalidate_resources('tuttlefile', urls)
        finally:
            sys.stdout, sys.stderr = oldout, olderr
        return rcode, out.getvalue()

    @isolate(['A'])
    def test_command_invalidate(self):
        """ Should display a message if there is no tuttlefile in the current directory"""
        project = """file://B <- file://A
            echo A creates B
            echo A creates B > B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0
        assert isfile('B')

        rcode, output = self.tuttle_invalide(urls=['file://B'])
        assert rcode == 0, output
        assert output.find('* file://B') >= 0, output
        assert not isfile('B'), output

    @isolate(['A'])
    def test_command_invalidate_with_dependencies(self):
        """ Should display a message if there is no tuttlefile in the current directory"""
        project = """file://B <- file://A
            echo A creates B
            echo A creates B > B

file://C <- file://B
            echo A creates C
            echo A creates C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0
        assert isfile('B')
        assert isfile('C')

        rcode, output = self.tuttle_invalide(urls=['file://B'])
        assert rcode == 0, output
        assert output.find('* file://B') >= 0, output
        assert output.find('* file://C') >= 0, output
        assert not isfile('B'), output
        assert not isfile('C'), output

    @isolate(['A'])
    def test_duration(self):
        """ Should display a message if there is no tuttlefile in the current directory"""
        project = """file://B <- file://A
            echo A creates B
            python -c "import time; time.sleep(1)"
            echo A creates B > B

file://C <- file://B
            echo A creates C
            python -c "import time; time.sleep(1.2)"
            echo A creates C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert isfile('B')
        assert isfile('C')

        rcode, output = self.tuttle_invalide(urls=['file://B'])
        assert rcode == 0, output
        assert output.find('* file://B') >= 0, output
        assert output.find('* file://C') >= 0, output
        assert output.find(' seconds') >= 0, output
        assert output.find('\n0 seconds') == -1, output
        assert not isfile('B'), output
        assert not isfile('C'), output

    @isolate
    def test_invalidate_no_tuttle_file(self):
        """ Should display a message when launching invalidate and there is tuttlefile in the current directory"""
        proc = Popen(['tuttle', 'invalidate', 'file://B'], stdout=PIPE)
        output = proc.stdout.read()
        rcode = proc.wait()
        assert rcode == 2, output
        assert output.find('No tuttlefile') >= 0, output

    @isolate
    def test_invalidate_nothing_have_run(self):
        """ Should display a message when launching invalidate and tuttle hasn't been run before :
            nothing to invalidate """
        project = """file://B <- file://A
            echo A creates B
            echo A creates B > B
            """
        rcode, output = self.tuttle_invalide(project=project)
        assert rcode == 2, output
        assert output.find("Tuttle has not run yet ! It has produced nothing, "
                           "so there is nothing to invalidate.") >= 0, output

    @isolate(['A'])
    def test_try_invalidate_bad_project(self):
        """ Should display a message if the tuttlefile is incorrect"""
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B
            """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0

        bad_project = """file://B <- file://A bad
            echo A produces B
            echo A produces B > B
            """
        rcode, output = self.tuttle_invalide(project=bad_project, urls=['file://B'])
        assert rcode == 2, output
        assert output.find('Invalidation has failed because tuttlefile is has errors') >= 0, output

    @isolate(['A'])
    def test_invalidate_no_urls(self):
        """ Should remove everything that is not in the last version of the tuttlefile """
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B

file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0

        new_project = """file://B <- file://A
            echo A produces B
            echo A produces B > B
            """
        rcode, output = self.tuttle_invalide(project=new_project)
        assert rcode == 0, output
        assert output.find('* file://C') >= 0, output
        assert output.find('no longer created') >= 0, output

    @isolate(['A'])
    def test_invalid_url_should_fail(self):
        """ Should display an error if the url passed in parameter is not valid or unknown scheme """
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B
            """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0

        rcode, output = self.tuttle_invalide(urls=['error://B'])
        assert rcode == 2, output
        assert output.find("'error://B'") >= 0, output

    @isolate(['A'])
    def test_unknown_resource_should_be_ignored(self):
        """ Should display a message if there is no tuttlefile in the current directory"""
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B
            """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0

        rcode, output = self.tuttle_invalide(urls=['file://C'])
        assert rcode == 0, output
        assert output.find("Ignoring file://C") >= 0, output

    @isolate(['A'])
    def test_not_produced_resource_should_be_ignored(self):
        """ Should display a message if there is no tuttlefile in the current directory"""
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B
            """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0

        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B

file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = self.tuttle_invalide(project=project, urls=['file://C'])
        assert rcode == 0, output
        assert output.find("Ignoring file://C : this resource has not been produced yet") >= 0, output

    @isolate(['A'])
    def test_invalidate_an_output_should_invalidate_all_outputs(self):
        """ Should invalidate all outputs if one is invalidated """
        project = """file://B file://C <- file://A
            echo A produces B
            echo A produces B > B
            echo A produces C
            echo A produces C > C
            """
        rcode, output = run_tuttle_file(project)
        assert rcode == 0

        rcode, output = self.tuttle_invalide(urls=['file://C'])
        assert rcode == 0, output
        assert output.find("* file://B") >= 0, output
        assert output.find("* file://C") >= 0, output
        assert output.find(BROTHER_INVALID.format("file://C")) >= 0, output

    @isolate(['A'])
    def test_new_primary_resources_should_not_be_invalidated(self):
        """ A primary resource that was produced with previous workflow shouldn't invalidate dependencies
        if it hasn't changed"""
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B

file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        print output
        assert rcode == 0, output

        project = """
file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = self.tuttle_invalide(project=project)
        assert rcode == 0, output
        assert output.find("Report has been updated to reflect") >= 0, output

    @isolate(['A'])
    def test_modified_new_primary_resources_should_invalidate_dependencies(self):
        """ If a resource has become a primary resource, but signature has not changed
        that was produced with previous workflow shouldn't invalidate dependencies
        if it hasn't changed"""
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B

file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        print output
        assert rcode == 0, output

        with open('B', "w") as f:
            f.write("Another  B")

        project = """
file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = self.tuttle_invalide(project=project)
        assert rcode == 0, output
        assert output.find("file://C") >= 0, output

    @isolate(['A'])
    def test_not_modified_new_primary_resources_should_not_invalidate_dependencies(self):
        """ If a resource has become a primary resource, but signature has not changed
        that was produced with previous workflow shouldn't invalidate dependencies
        if it hasn't changed"""
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B

file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        print output
        assert rcode == 0, output

        project = """
file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = self.tuttle_invalide(project=project)
        assert rcode == 0, output
        assert output.find("Report has been updated to reflect") >= 0, output

    @isolate(['A'])
    def test_adding_an_output_invalidates_process(self):
        """ Adding an ingutput to a process that have succeeded should invalidate the whole process,
        thus invalidate all other resources """
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B
            echo A produces C
            echo A produces C > C
"""
        rcode, output = run_tuttle_file(project)
        print output
        assert rcode == 0, output

        project = """file://B file://C<- file://A
            echo A produces B
            echo A produces B > B
            echo A produces C
            echo A produces C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("file://B") >= 0, output
        assert output.find("A produces B") >= 0, output
        assert output.find("A produces C") >= 0, output

    @isolate(['A', 'B'])
    def test_removing_an_output_invalidates_process(self):
        """ Removing an output to a process that have succeeded should invalidate the whole process,
        thus invalidating all resources """
        project = """file://B file://C <- file://A
            echo A produces B
            echo A produces B > B
            echo A produces C
            echo A produces C > C
"""
        rcode, output = run_tuttle_file(project)
        print output
        assert rcode == 0, output

        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B
            echo A produces C
            echo A produces C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("file://B") >= 0, output
        assert output.find("file://C") >= 0, output
        assert output.find("A produces B") >= 0, output
        assert output.find("A produces C") >= 0, output

    @isolate(['A'])
    def test_workflow_must_be_run_after_resource_invalidation(self):
        """ After invalidation of a resource, tuttle run should re-produce this resource """
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B

file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

        rcode, output = self.tuttle_invalide(urls=["file://C"])
        assert rcode == 0, output
        assert output.find("file://C") >= 0, output
        rcode, output = run_tuttle_file(project)
        assert output.find("Nothing to do") == -1, output
        assert output.find("B produces C") >= 0, output

    @isolate(['A'])
    def test_workflow_must_be_run_after_resource_invalidation_in_cascade(self):
        """ After invalidation of a resource, tuttle run should re-produce this resource and the dependencies"""
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

        rcode, output = self.tuttle_invalide(urls=["file://A"])
        assert rcode == 0, output
        assert output.find("Ignoring file://A") >= 0, output

    @isolate(['A'])
    def test_process_in_error_should_be_invalidated(self):
        """ If a process failed, its dependencies should be invalidated """
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B
            an error
"""
        rcode, output = run_tuttle_file(project)
        print output
        assert rcode == 2, output
        assert isfile('B')

        rcode, output = self.tuttle_invalide(project=project)
        assert rcode == 0, output
        assert output.find("file://B") >= 0, output
        assert not isfile('B'), output

    @isolate(['A'])
    def test_a_failing_process_without_output_should_be_invalidated(self):
        """  When a process fail, Tuttle should exit with status code 2, even if the process has no outputs"""
        project = """file://B <- file://A
    echo A produces B
    echo B > B

<- file://B
    error
    echo This should not be written
    echo C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 2
        assert isfile('B')
        assert not isfile('C')

        report_path = join('.tuttle', 'report.html')
        assert isfile(report_path)
        report = open(report_path).read()
        title_match_failure = search(r'<h1>.*Failure.*</h1>', report, DOTALL)
        assert title_match_failure, report

        rcode, output = self.tuttle_invalide()
        assert rcode == 0

        report = open(report_path).read()
        title_match_failure = search(r'<h1>.*Failure.*</h1>', report, DOTALL)
        assert not title_match_failure, title_match_failure.group()

    @isolate(['A', 'B'])
    def test_dont_invalidate_outputless_process(self):
        """ Don't invalidate a successful process without outputs(from bug) """
        first = """file://C <- file://A
    echo A produces C > C

<- file://B
    echo Action after B is created
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output

        rcode, output = self.tuttle_invalide()
        assert rcode == 0, output

        rcode, output = run_tuttle_file(first)
        assert rcode == 0
        assert output.find("Nothing to do") >= 0, output
        assert output.find("Action") == -1, output

    @isolate(['A'])
    def test_changes_in_the_graph_without_removing_resource(self):
        """ If the graph changes without removing resource tuttle should display a message
            event if the removed resource is used elsewhere (from bug) """

        first = """ <- file://A
    echo Action after A is created.

file://B <- file://A
    echo B > B 

file://C <- file://B
    echo C > C
"""
        rcode, output = run_tuttle_file(first)
        print output
        assert rcode == 0, output

        second = """ <- file://A
    echo Action after A is created.

file://C <- file://B
    echo C > C
"""
        rcode, output = self.tuttle_invalide(project=second)
        assert rcode == 0, output
        assert output.find("Report has been updated to reflect") >= 0, output

    @isolate(['A', 'B'])
    def test_dont_mess_up_with_outputless_process(self):
        """ Successful outputless process must not run again, even if some other
        process have the same input (from bug) """
        first = """file://C <- file://A
    echo A produces C > C

<- file://A
    echo Action from A
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output

        rcode, output = run_tuttle_file(first)
        assert rcode == 0
        assert output.find("Nothing to do") >= 0, output
        assert output.find("Action") == -1, output

