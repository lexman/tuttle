from datetime import timedelta
from os import path, error
from re import compile


KB = 1024
MB = 1024 * 1024
GB = 1024 * 1024 * 1024


def round_after_dot(num, precision):
    meaningful = 10 * num / precision
    return meaningful * 0.1


def nice_size(size):
    if size < KB:
        return "{} B".format(size)
    elif size < MB:
        return "{} KB".format(round_after_dot(size, KB))
    elif size < GB:
        return "{} MB".format(round_after_dot(size, MB))
    else:
        return "{} GB".format(round_after_dot(size, GB))


def nice_file_size(filename, running):
    if running:
        return "running"
    if not filename:
        return ""
    try:
        file_size = path.getsize(filename)
        if file_size == 0:
            return "empty"
        return nice_size(file_size)
    except error:
        return ""


ONE_MINUTE = timedelta(minutes=1)
ONE_HOUR = timedelta(hours=1)
ONE_DAY = timedelta(days=1)


def nice_duration(duration):
    duration_in_s = int(duration)
    delta = timedelta(seconds=duration_in_s)
    if delta < ONE_MINUTE:
        return "{}s".format(delta.seconds)
    elif delta < ONE_HOUR:
        minutes = duration_in_s / 60
        seconds = duration_in_s % 60
        return "{}min {}s".format(minutes, seconds)
    elif delta < ONE_DAY:
        hours = duration_in_s / 3600
        minutes = (duration_in_s - hours * 3600) / 60
        return "{}h {}min".format(hours, minutes)
    else:
        hours = (duration_in_s - delta.days * 3600 * 24) / 3600
        return "{}d {}h".format(delta.days, hours)


DURATION_REGEX = compile("^((?P<days>\d+)\s*d)?\s*((?P<hours>\d+)\s*h)?\s*((?P<min>\d+)\s*min)?\s*((?P<sec>\d+)\s*s)?$")


def group_value(match_result, group_name):
    if match_result.group(group_name):
        return int(match_result.group(group_name))
    return 0


def parse_duration(expression):
    # Not a simple int, we have to parse
    m = DURATION_REGEX.match(expression)
    if m:
        sec = group_value(m, 'sec')
        min = group_value(m, 'min')
        hours = group_value(m, 'hours')
        days = group_value(m, 'days')
        return ((((days * 24) + hours ) * 60) + min) * 60 + sec
    raise ValueError('"{}" is not a valid duration'.format(expression))
