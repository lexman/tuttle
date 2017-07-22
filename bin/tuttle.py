#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
from os.path import abspath, dirname, join

if getattr(sys, 'frozen', False):
    # frozen
    tuttle_module = join(dirname(abspath(sys.executable)), '..', '..', 'tuttlelib')
else:
    # unfrozen
    tuttle_module = join(dirname(abspath(__file__)), '..', '..', 'tuttlelib')
sys.path.insert(0, tuttle_module)

from tuttlelib.entry_points import tuttle_main

if __name__ == '__main__':
    sys.exit(tuttle_main())