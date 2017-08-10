# -*- coding: utf-8 -*-
import os

from cStringIO import StringIO
from nose.plugins.skip import SkipTest

from tuttle.workflow_builder import MalformedTuttlepassError, tuttlepass_file, ResourceAuthenticator
from tuttle.utils import EnvVar


class TestAuthentication:

    def test_path_on_linux(self):
        """ On linux, default path must be on ~/.tuttlepass """
        if os.name != 'posix':
            raise SkipTest("This test is valid only on Linux")
        assert tuttlepass_file().endswith("/.tuttlepass"), tuttlepass_file()

    def test_path_on_windows(self):
        """ On Windows, default path must be on XXX """
        if os.name != 'nt':
            raise SkipTest("This test is valid only on Windows")
        assert tuttlepass_file().endswith("\.tuttlepass"), tuttlepass_file()

    def test_path_with_env_var(self):
        """ if environnement variable TUTTLEPASSPAHT """
        with EnvVar('TUTTLEPASSFILE', 'bar'):
            assert tuttlepass_file() == "bar"

    def test_bad_regexp(self):
        rules = """        
http://g[ithub.com/\tuser\tpassword
        """
        passfile = StringIO(rules)
        try:
            auth = ResourceAuthenticator(passfile)
            assert False, "should not be here"
        except MalformedTuttlepassError as e:
            assert e.message.find("Parse error on regular expression") > -1, e.message

    def test_field_missing(self):
        rules = """        
http://github.com/\tuser
        """
        passfile = StringIO(rules)
        try:
            auth = ResourceAuthenticator(passfile)
            assert False, "should not be here"
        except MalformedTuttlepassError as e:
            assert e.message.find("wrong number of fields") > -1, e.message

    def test_two_many_fields(self):
        rules = """        
http://github.com/\tuser\tpassword\textra
        """
        passfile = StringIO(rules)
        try:
            auth = ResourceAuthenticator(passfile)
            assert False, "should not be here"
        except MalformedTuttlepassError as e:
            assert e.message.find("wrong number of fields") > -1, e.message

    def test_comment_is_allowed(self):
        """ When there is a comment, spaces before # are not considered as part of the password """
        rules = """        
http://github.com/\tuser\tpassword # comment 
        """
        passfile = StringIO(rules)
        auth = ResourceAuthenticator(passfile)
        user, password = auth.get_auth("http://github.com/")
        assert user == "user", user
        assert password == "password", password

    def test_regexp(self):
        """ When there is a comment, spaces before # are not considered as part of the password """
        rules = """        
http://.*github.com/\tuser\tpassword 
        """
        passfile = StringIO(rules)
        auth = ResourceAuthenticator(passfile)
        user, password = auth.get_auth("http://github.com/")
        assert user == "user", user
        assert password == "password", password

        user, password = auth.get_auth("http://www.github.com/")
        assert user == "user", user
        assert password == "password", password

    def test_several_regexp(self):
        """ url can be captured by the second regex """
        rules = """        
http://.*github.com/\tuser\tpassword
http://.*python.org\tuser2\tpassword2
        """
        passfile = StringIO(rules)
        auth = ResourceAuthenticator(passfile)
        print auth._rules
        user, password = auth.get_auth("http://python.org")
        assert user == "user2", user
        assert password == "password2", "'{}'".format(password)

    def test_partial_regexp(self):
        """ When there is a comment, spaces before # are not considered as part of the password """
        rules = """        
github\tuser\tpassword 
        """
        passfile = StringIO(rules)
        auth = ResourceAuthenticator(passfile)
        user, password = auth.get_auth("http://github.com/")
        assert user == "user", user
        assert password == "password", password

    def test_no_match(self):
        """ When there is a comment, spaces before # are not considered as part of the password """
        rules = """        
github\tuser\tpassword 
        """
        passfile = StringIO(rules)
        auth = ResourceAuthenticator(passfile)
        user, password = auth.get_auth("http://linux.com/")
        assert user is None, user
        assert password is None, password
