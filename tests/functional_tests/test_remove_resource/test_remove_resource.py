#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from tests.functional_tests import FunctionalTestBase, isolate


class TestRemoveResource(FunctionalTestBase):

    @isolate(['A'])
    def test_remove_resource(self):
        """If a resource is removed from a tuttlefile, it should be deleted"""
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
        assert result.find("* file://B") >= 0
        assert result.find("* file://C") >= 0
        assert result.find("* file://D") == -1
