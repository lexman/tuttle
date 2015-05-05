# -*- coding: utf-8 -*-

from tuttle.report.html_repport import nice_size


class TestReport():

    def test_nice_size_B(self):
        """ A number below 1 000 B should be expressed in B"""
        nice = nice_size(12)
        assert nice == "12 B", nice

    def test_nice_size_KB(self):
        """ A number below 1 000 000 B should be expressed in B"""
        nice = nice_size(12034)
        assert nice == "11 KB", nice

    def test_nice_size_MB(self):
        """ A number below 1 000 000 0000 B should be expressed in B"""
        nice = nice_size(12056000)
        assert nice == "11 MB", nice

    def test_nice_size_GB(self):
        """ A number below 1 000 000 0000 000 B should be expressed in B"""
        nice = nice_size(12049000000)
        assert nice == "11 GB", nice
