# -*- coding: utf-8 -*-
from os.path import isfile

from os import path
from tests.functional_tests import isolate, run_tuttle_file


class TestInvalidateResource():

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

