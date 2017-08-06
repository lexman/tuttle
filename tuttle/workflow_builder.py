# -*- coding: utf8 -*-
import re
from os.path import expanduser, exists

from tuttle.error import TuttleError
from tuttle.resource import FileResource
from tuttle.processors import *
from tuttle.process import Process
from tuttle.addons.csv_addon import CSV2SQLiteProcessor
from tuttle.addons.net import DownloadProcessor, HTTPResource
from tuttle.addons.postgres import PostgreSQLResource, PostgresqlProcessor
from tuttle.addons.python import PythonProcessor
from tuttle.addons.s3 import S3Resource
from tuttle.addons.sqlite import SQLiteProcessor, SQLiteResource
import os



class MalformedTuttlepassError(TuttleError):
    pass


def tuttlepass_file():
    if 'TUTTLEPASSFILE' in os.environ:
        return os.environ['TUTTLEPASSFILE']
    else:
        return expanduser('~/.tuttlepass')


class ResourceAuthenticator:

    def __init__(self, lines_reader):
        self._rules = [rule for rule in ResourceAuthenticator.read_rules(lines_reader)]

    def fill_rules(self, line_reader):
        self._rules = [rule for rule in ResourceAuthenticator.read_rules(line_reader)]

    def get_auth(self, url):
        for regex, user, password in self._rules:
            if regex.search(url):
                return user, password
        return None, None

    @staticmethod
    def empty_line(line):
        for ch in line:
            if ch != " " and ch != "\t" and ord(ch) != 10:
                return False
        return True

    @staticmethod
    def read_rules(file_in):
        line_no = 1
        try:
            for line in file_in:
                pos_sharp = line.find('#')
                if pos_sharp > -1:
                    line = line[:pos_sharp].strip()
                else:
                    line = line.strip()
                if not ResourceAuthenticator.empty_line(line):
                    url_regex, user, password = line.split("\t")
                    yield (re.compile(url_regex), user, password)
                line_no += 1
        except:
            msg = "Parse error on tuttlepass file at line {}".format(line_no)
            raise MalformedTuttlepassError(msg)


class WorkflowBuilder():
    """A helper class to build Process classes from the name of processors and resources"""
    
    def __init__(self):
        self._resources_definition = {}
        self._processors = {}
        self._resource_authenticator = None
        self.init_resource_authenticator()
        self.init_resources_and_processors()

    def init_resource_authenticator(self):
        pass_file = tuttlepass_file()
        if exists(pass_file):
            with open(tuttlepass_file()) as f:
                self._resource_authenticator = ResourceAuthenticator(f)
        else:
            self._resource_authenticator = ResourceAuthenticator([])

    def init_resources_and_processors(self):
        self._resources_definition['file'] = FileResource
        self._resources_definition['http'] = HTTPResource
        self._resources_definition['https'] = HTTPResource
        self._resources_definition['sqlite'] = SQLiteResource
        self._resources_definition['pg'] = PostgreSQLResource
        self._resources_definition['s3'] = S3Resource
        self._processors['shell'] = ShellProcessor()
        self._processors['bat'] = BatProcessor()
        self._processors['python'] = PythonProcessor()
        self._processors['download'] = DownloadProcessor()
        self._processors['sqlite'] = SQLiteProcessor()
        self._processors['postgresql'] = PostgresqlProcessor()
        self._processors['csv2sqlite'] = CSV2SQLiteProcessor()
        if os.name == "nt":
            self._processors['default'] = self._processors['bat']
        else:
            self._processors['default'] = self._processors['shell']

    def extract_scheme(self, url):
        """Extract the scheme from an url
        url is supposed to be stripped from spaces
        """
        separator_pos = url.find('://')
        if separator_pos == -1:
            return False
        url_scheme = url[:separator_pos]
        return url_scheme

    def url_is_empty(self, url):
        """
        :param url:
        :return: True if the url consist only in the scheme without further information
        """
        separator_pos = url.find('://')
        return separator_pos == (len(url) - len('://'))

    def build_resource(self, url):
        scheme = self.extract_scheme(url)
        if scheme is False or scheme not in self._resources_definition:
            return None
        if self.url_is_empty(url):
            return None
        ResDefClass = self._resources_definition[scheme]
        resource = ResDefClass(url)
        user, password = self._resource_authenticator.get_auth(url)
        resource.set_authentication(user, password)
        return resource
    
    def build_process(self, processor, file_name, line_num):
        if processor in self._processors:
            return Process(self._processors[processor], file_name, line_num)
        else:
            return False

    def get_or_build_resource(self, url, resources):
        if url not in resources:
            resource = self.build_resource(url)
            resources[url] = resource
        else:
            resource = resources[url]
        return resource
