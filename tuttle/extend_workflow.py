#!/usr/bin/env python
# -*- coding: utf8 -*-


from jinja2.environment import Environment
from jinja2.exceptions import UndefinedError
from jinja2.loaders import FileSystemLoader
from jinja2.runtime import StrictUndefined
from os.path import abspath, exists, join
from tuttle.utils import CurrentDir


class ExtendError(Exception):
    pass


def get_a_name(prefix):
    # TODO : not scalable if called a lot of times
    i = 1
    name = abspath(join('extensions', "{}{}".format(prefix, i)))
    while exists(name):
        name = abspath(join('extensions', "{}{}".format(prefix, i)))
        i += 1
    return name


def extract_variables(variables):
    res = {}
    for var in variables:
        try:
            name, value = var.split("=", 2)
        except ValueError:
            msg = 'Can\'t extract variable from parameter "{}"'.format(var)
            raise ExtendError(msg)
        res[name] = value
    return res


def load_template(template):
    try:
        jinja_env = Environment(loader=FileSystemLoader("."), undefined=StrictUndefined)
        t = jinja_env.get_template(template)
    except IOError:
        msg = 'Can\'t find template file "{}"'.format(template)
        raise ExtendError(msg)
    return t


def get_tuttle_env(env_vars):
    try:
        env = env_vars['TUTTLE_ENV']
    except KeyError:
        msg = 'Can\'t find workspace... Maybe your are not running tuttle-extend-workflow from a preprocessor in a ' \
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


def extend_workflow(template, variables, name, env_vars):
    t = load_template(template)
    vars_dic = extract_variables(variables)
    tuttle_env = get_tuttle_env(env_vars)
    render_extension(name, t, tuttle_env, vars_dic)
