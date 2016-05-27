#!/usr/bin/env python
# -*- coding: utf8 -*-

from jinja2.environment import Environment
from jinja2.exceptions import UndefinedError
from jinja2.runtime import StrictUndefined
from os.path import abspath, exists, join
from os import environ
from tuttle.utils import CurrentDir


class ExtendError(Exception):
    pass


def get_a_name(prefix):
    # TODO : not scalable if called a lot of times
    name = abspath(join('extensions', prefix))
    i = 1
    while exists(name):
        i += 1
        name = abspath(join('extensions', "{}{}".format(prefix, i)))
    return name


def extract_variables(variables):
    res = {}
    it = iter(variables)
    try:
        var = next(it)
        while True:
            name, value = var.split("=", 2)
            if name.endswith("[]"):
                name = name[:-2]
                array = [value]
                res[name] = array
                var = next(it)
                while var.find('=') == -1:
                    array.append(var)
                    var = next(it)
            else:
                res[name] = value
                var = next(it)
    except ValueError:
        msg = 'Can\'t extract variable from parameter "{}"'.format(var)
        raise ExtendError(msg)
    except StopIteration:
        pass
    return res


def load_template(template):
    try:
        jinja_env = Environment(undefined=StrictUndefined)
        with open(template, 'rb') as ftpl:
            t = jinja_env.from_string(ftpl.read().decode('utf8'))
    except IOError:
        msg = 'Can\'t find template file "{}"'.format(template)
        raise ExtendError(msg)
    return t


def get_tuttle_env(env_vars):
    try:
        env = env_vars['TUTTLE_ENV']
    except KeyError:
        msg = 'Can\'t find workspace... Maybe your are not extending a workflow from a preprocessor in a ' \
              'tuttle project'
        raise ExtendError(msg)
    return env


def render_extension(name, t, tuttle_env, vars_dic):
    with CurrentDir(tuttle_env):
        with open(get_a_name(name), 'w') as ext_file:
            try:
                content = t.render(**vars_dic)
            except UndefinedError as e:
                msg = 'Missing value for a template variable.\n{}'.format(e.message)
                raise ExtendError(msg)
            ext_file.write(content.encode('utf8)'))


def extend_workflow(template, name='extension', env_vars=environ, **variables):
    t = load_template(template)
    tuttle_env = get_tuttle_env(env_vars)
    render_extension(name, t, tuttle_env, variables)
