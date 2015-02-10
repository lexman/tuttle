#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys


agg = open("codes_for_aggregated_regions.tsv", "r")


def get_aggregated_code(name):
    pass

def main():
    f = open("old_regions.tsv", "r")    
    for line in f:
        code, _, _, _, name = line.strip().split("\t")
        print code

if __name__ == "__main__":
    main()
        
     