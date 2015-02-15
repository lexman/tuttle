#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from tests.functional_tests import FunctionalTestBase


class TestRemoveResource(FunctionalTestBase):

    def test_remove_resource(self):
        """If a resource is removed from a tuttlefile, it should be deleted"""
        self.work_dir_from_module(__file__)
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
        self.write_tuttlefile(first)
        result = self.run_tuttle()
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
        self.write_tuttlefile(second)
        result = self.run_tuttle()
        print( result)
        assert result.find("* file://B") >= 0
        assert result.find("* file://C") >= 0
        assert result.find("* file://D") == -1
        print result

    def tearDown(self):
        try:
            self.reset()
            self._rm('B')
            self._rm('C')
            self._rm('D')
        finally:
            super(TestRemoveResource, self).tearDown()