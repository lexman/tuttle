from datetime import timedelta
from os import path, error


KB = 1024
MB = 1024 * 1024
GB = 1024 * 1024 * 1024


ONE_MINUTE = timedelta(minutes=1)
ONE_HOUR = timedelta(hours=1)
ONE_DAY = timedelta(days=1)


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


def nice_duration(seconds):
    delta = timedelta(seconds=seconds)
    if delta < ONE_MINUTE:
        return "{}s".format(delta.seconds)
    elif delta < ONE_HOUR:
        minutes = seconds / 60
        sec = seconds % 60
        return "{}min {}s".format(minutes, sec)
    elif delta < ONE_DAY:
        hours = seconds / 3600
        minutes = (seconds - hours * 3600) / 60
        return "{}h {}min".format(hours, minutes)
    else:
        hours = (seconds - delta.days * 3600 * 24) / 3600
        return "{}d {}h".format(delta.days, hours)