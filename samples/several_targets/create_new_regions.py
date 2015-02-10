#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys

new_num_region = 61

def main(input_stream):
    global new_num_region
    for line in input_stream:
        old_regs = line.strip().split(',')
        if len(old_regs) > 1:
            print "{}\t{}".format(new_num_region, ' - '.join(old_regs))

if __name__ == "__main__":
    main(sys.stdin)
        
        
    