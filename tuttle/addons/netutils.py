# -*- coding: utf8 -*-
from socket import gethostbyname, error


def hostname_resolves(hostname):
    try:
        print gethostbyname(hostname)
        return True
    except error:
        return False
