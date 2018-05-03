# -*- coding: utf-8 -*-
from os.path import isfile, join

from os import path, remove

from nose.plugins.skip import SkipTest

from tests import online
from tests.functional_tests import isolate, run_tuttle_file
from tuttle.invalidation import NO_LONGER_CREATED, NOT_SAME_INPUTS, PROCESS_HAS_CHANGED, PROCESSOR_HAS_CHANGED
from tuttle.project_parser import ProjectParser


class TestInvalidateResource():

    def get_workflow(self, project_source):
        pp = ProjectParser()
        pp.set_project(project_source)
        return pp.parse_project()

    @isolate(['A'])
    def test_remove_resource(self):
        """If a resource is removed from a tuttlefile, it should be invalidated"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    echo B produces C
    echo C > C

file://D <- file://A
    echo A produces D
    echo D > D
"""
        rcode, output = run_tuttle_file(first)
        assert path.exists('B')
        assert path.exists('C')
        assert path.exists('D')
        second = """file://C <- file://A
    echo A produces C
    echo C > C

file://D <- file://A
    echo A produces D
    echo D > D
"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 0
        assert output.find("* file://B") >= 0, output
        assert output.find("* file://C") >= 0, output
        assert output.find("* file://D") == -1, output

    @isolate(['A', 'B'])
    def test_resource_should_be_created_by_tuttle(self):
        """If a resource was not created by tuttle, it should be invalidated"""
        first = """file://B <- file://A
    echo A produces B
    echo B > B
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0
        assert output.find("* file://B") >= 0, output

    @isolate(['A'])
    def test_code_changes(self):
        """ A resource should be invalidated if the code that creates it changes"""
        project1 = """file://B <- file://A
        echo A creates B > B
        """
        rcode, output = run_tuttle_file(project1)
        assert isfile('B')
        project2 = """file://B <- file://A
        echo A creates B in another way> B
        """
        rcode, output = run_tuttle_file(project2)
        assert rcode == 0
        assert output.find("* file://B") >= 0, output
        assert output.find(PROCESS_HAS_CHANGED) >= 0, output

    @isolate(['A'])
    def test_removed_resource(self):
        """ A resource should be invalidated if it is not created anymore
        """
        project1 = """file://B <- file://A
    echo A creates B > B

file://C <- file://A
    echo A creates C > C
"""
        rcode, output = run_tuttle_file(project1)
        assert isfile('B')
        project2 = """file://B <- file://A
    echo A creates B > B
        """
        rcode, output = run_tuttle_file(project2)
        assert rcode == 0
        assert output.find("* file://C") >= 0, output
        assert output.find(NO_LONGER_CREATED) >= 0, output

    @isolate(['A', 'B'])
    def test_resource_dependency_change(self):
        """ A resource should be invalidated if it does not depend on the same resource anymore
        """
        project1 = """file://C <- file://A, file://B  
    echo A creates C > C
"""
        rcode, output = run_tuttle_file(project1)
        assert isfile('B')
        project2 = """file://C <- file://A
    echo A creates C > C
"""
        rcode, output = run_tuttle_file(project2)
        assert rcode == 0
        assert output.find("* file://C") >= 0, output
        assert output.find(NOT_SAME_INPUTS) >= 0, output

    @isolate(['A', 'B'])
    def test_resource_is_now_created_by_tuttle(self):
        """ If a resource used to be primary but is now created by tuttle, it should be invalidated """
        first = """file://C <- file://B
    echo B produces C
    echo C > C
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0
        second = """file://B <- file://A
    echo A produces B
    echo B > B

file://C <- file://B
    echo B produces C
    echo C > C"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 0
        assert output.find("* file://B") >= 0, output

    @isolate(['A', 'B'])
    def test_resource_becomes_primary(self):
        """ If a resource becomes primary, it should not be invalidated """
        first = """file://B <- file://A
            echo A produces B
            echo B > B

        file://C <- file://B
            echo B produces C
            echo C > C"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0
        second = """file://C <- file://B
            echo B produces C
            echo C > C
        """
        rcode, output = run_tuttle_file(second)
        assert rcode == 0
        assert output.find("* file://B") == -1, output
        assert output.find("Report has been updated") >= 0, output

    @isolate(['A'])
    def test_modified_primary_resource_should_invalidate_dependencies(self):
        """ If a primary resource is modified, it should invalidate dependencies"""
        project = """file://B <- file://A
    echo A produces B
    echo B > B
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        with open('A', 'w') as f:
            f.write('A has changed')
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find('* file://A') == -1, output
        assert output.find('* file://B') >= 0, output
        assert output.find('A produces B') >= 0, output
        assert output.find("file://A which has changed") >= 0, output

    @isolate(['A'])
    def test_modified_primary_resource_should_invalidate_dependencies_in_cascade(self):
        """ If a primary resource is modified, it should invalidate direct dependencies
        and dependencies of dependencies """
        project = """file://B <- file://A
    echo A produces B
    echo A produces B > B

file://C <- file://B
    echo B produces C
    echo B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        with open('A', 'w') as f:
            f.write('A has changed')
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find('* file://A') == -1, output
        assert output.find('file://A which has changed') >= 0, output
        assert output.find('* file://B') >= 0, output
        assert output.find('* file://C') >= 0, output
        assert output.find('A produces B') >= 0, output
        assert output.find('B produces C') >= 0, output

    @isolate(['A', 'B'])
    def test_should_display_invalid_resource_only_once(self):
        """ If a resource has several reasons to be invalidated, it should be displayed only once"""
        project = """file://C <- file://A file://B
    echo A and B produces C
    echo A and B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        with open('A', 'w') as f:
            f.write('A has changed')
        with open('B', 'w') as f:
            f.write('B has changed')
        project = """file://C <- file://A file://B
    echo A and B produces C differently
    echo A and B produces C differently > C
"""

        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        pos_start = output.find('* file://C')
        pos_end = pos_start + len('* file://C')
        assert pos_start >= 0, output
        pos2 = output.find('* file://C', pos_end)
        assert pos2 == -1, output

    @isolate(['A'])
    def test_should_not_display_invalid_twice(self):
        """ Fixes a bug where resources where displayed twice"""
        project1 = """file://B <- file://A
    echo A produces B
    echo A produces B > B
"""
        rcode, output = run_tuttle_file(project1)
        assert rcode == 0, output

        project1 = """file://B <- file://A
    echo A produces B somehow differently
    echo A produces B somehow differently > B
"""
        rcode, output = run_tuttle_file(project1)
        assert rcode == 0, output
        pos_start = output.find('* file://B')
        pos_end = pos_start + len('* file://B')
        assert pos_start >= 0, output
        assert output.find('* file://B', pos_end) == -1, output
        assert output.find('* has not been', pos_end) == -1, output

    @isolate(['A'])
    def test_invalidation_in_cascade(self):
        """ When a resource is invalidated all resulting resources should be invalidated too
        """

        project1 = """file://B <- file://A
    echo A produces B > B

file://C <- file://B
    echo B produces C > C
"""
        rcode, output = run_tuttle_file(project1)
        assert rcode == 0, output

        project2 = """file://B <- file://A
    echo A produces another B > B

file://C <- file://B
    echo B produces C > C
"""
        rcode, output = run_tuttle_file(project2)
        assert rcode == 0, output
        assert output.find('* file://B - Process code has changed') > -1, output
        assert output.find('* file://C') > -1, output

    @isolate(['A'])
    def test_should_run_after_invalidation(self):
        """  """
        project = """file://B <- file://A
            echo A produces B
            echo A produces B > B

file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

        project = """file://B <- file://A
            echo A produces another B
            echo A produces B > B

file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("file://B") >= 0, output
        assert output.find("file://C") >= 0, output
        assert output.find("A produces another B") >= 0, output
        assert output.find("B produces C") >= 0, output

    @isolate(['A'])
    def test_invalidation_should_resist_remove_errors(self):
        """ If removing a resource raises an error, tuttle should display a warning"""
        if not online:
            raise SkipTest("Offline")
        project = """http://www.google.com <- file://A
            echo As if I could publish to the main page of google...
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output

        project = """http://www.google.com <- file://A
            echo process changed
"""
        rcode, output = run_tuttle_file(project)
        assert rcode == 0, output
        assert output.find("http://www.google.com") >= 0, output
        assert output.find("Warning") >= 0, output
        assert output.find("should not be considered valid") >= 0, output

    @isolate(['A'])
    def test_processor_has_been_fixed(self):
        """ Changing the processor should invalidate dependencies """
        first = """file://B <- file://A
    print("some python code")
    open('B', 'w').write('A produces B')
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 2, output

        second = """file://B <- file://A ! python
    print("some python code")
    open('B', 'w').write('A produces B')
"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 0, output
        assert output.find("file://B") >= 0, output
        assert isfile('B')
        assert output.find(PROCESSOR_HAS_CHANGED) >= 0, output

    @isolate(['A'])
    def test_processor_or_process_has_been_fixed(self):
        """ Changing the processor of a process should invalidate dependencies """
        first = """file://B <- file://A
            print("some python code")
            open('A', 'w').write('A produces B')
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 2, output

        second = """file://B <- file://A ! python
            print("some python code")
            open('B', 'w').write('A produces B')
"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 0, output
        assert output.find("file://B") >= 0, output
        assert isfile('B')
        assert output.find(PROCESS_HAS_CHANGED) >= 0, output

    @isolate(['A'])
    def test_remove_primary(self):
        """ Remove the first process and transform a resource in a primary resource should be
        considered as processing """
        first = """file://B <- file://A
            echo A produces another B
            echo A produces B > B

file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output

        second = """file://C <- file://B
            echo B produces C
            echo B produces C > C
"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 0, output
        assert output.find("Report has been updated") >= 0, output
        report = open(join('.tuttle', 'report.html')).read()
        assert report.find('file://A') == -1, report
        dump = open(join('.tuttle', 'last_workflow.pickle')).read()
        assert report.find('file://A') == -1, report

    @isolate(['A'])
    def test_dont_invalidate_if_errors(self):
        """ When there is a process in error, invalidation prior to running must not occur """
        first = """file://B <- file://A
            echo A produces B
            echo A produces B > B

file://C <- file://A
            error
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 2, output

        second = """file://B <- file://A
            echo Not fixing the right thing
            echo A produces B > B

file://C <- file://A
            error
"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 2
        assert output.find("Workflow already failed") >= 0, output

    @isolate(['A'])
    def test_rerun_outputless_process_if_code_changed(self):
        """ A change in a process without output should re-run the process (from bug) """
        first = """ <- file://A
            echo Action after A is created
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output

        second = """ <- file://A
            echo Another action after A is created
"""
        rcode, output = run_tuttle_file(second)
        assert rcode == 0
        assert output.find("Another") >= 0, output

    @isolate(['A'])
    def test_rerun_outputless_process_if_code_changed(self):
        """ An outputless process should not re-run if it hasn't changed """
        first = """ <- file://A
            echo Action after A is created
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output

        rcode, output = run_tuttle_file(first)
        assert rcode == 0
        assert output.find("Nothing to do") >= 0, output

    @isolate(['A'])
    def test_invalidate_all_outputs_from_a_process_if_one_missing(self):
        """ If an output of a successfull process is missing, all others outputs should be removed
        and the process should re-run """
        first = """file://C file://B <- file://A
    echo A produces B
    echo A produces B > B
    echo A produces C
    echo A produces C > C
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        remove('B')

        rcode, output = run_tuttle_file(first)
        assert rcode == 0
        assert output.find("file://C") >= 0, output
        assert output.find("A produces B") >= 0, output
        assert output.find("A produces C") >= 0, output

    @isolate(['A'])
    def test_change_a_resource(self):
        """ If a resource (not primary) has changed outside tuttle, it should be invalidated if checking integrity"""
        first = """file://C file://B <- file://A
    echo A produces B
    echo A produces B > B
    echo A produces C
    echo A produces C > C

file://D <- file://C   
    echo C produces D
    echo C produces D > D
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert path.exists('B')
        assert path.exists('C')
        with open('B', 'w') as f:
            f.write('B has changed')

        rcode, output = run_tuttle_file(first, check_integrity=True)
        assert rcode == 0
        assert output.find("file://B") >= 0, output
        assert output.find("file://C") >= 0, output
        assert output.find("file://D") >= 0, output
        assert output.find("A produces B") >= 0, output
        assert output.find("A produces C") >= 0, output
        assert output.find("C produces D") >= 0, output

    @isolate(['A'])
    def test_change_a_resource(self):
        """ Don't mind a resource (not primary) that have changed outside tuttle, if NOT checking integrity"""
        first = """file://C file://B <- file://A
    echo A produces B
    echo A produces B > B
    echo A produces C
    echo A produces C > C

file://D <- file://C   
    echo C produces D
    echo C produces D > D
"""
        rcode, output = run_tuttle_file(first)
        assert rcode == 0, output
        assert path.exists('B')
        assert path.exists('C')
        with open('B', 'w') as f:
            f.write('B has changed')

        rcode, output = run_tuttle_file(first, check_integrity=False)
        assert rcode == 0
        assert output.find("Nothing to do") >= 0, output
