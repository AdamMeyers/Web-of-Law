#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## This script runs through one directory and creates one txt and one
## offset file for each json file in that directory.
## You can call this with one or two arguments.
## The first argument should be the directory containing the input
## json files.
## The second (optional) arguments should be True or False.
## True means "always use the html field" in the json file
## and False means use the best field according to a system of defaults.
## By default, we are currently using the html field (the False
## setting), due to some encoding bugs at Court listener, but
## eventually expect to switch.

from find_case_citations5 import *
import sys
import os

def main (args):
    if len(args)<2:
        print('This function requires one argument: The name of a file -- the full path, but no extensions')
    else:
        base_file = args[1]
        if os.sep in base_file:
            sep_index = base_file.rindex(os.sep)
            file_id = base_file[sep_index+1:]
        else:
            file_id = base_file
        find_case_citations(base_file+'.txt',base_file+'.case9',file_id,base_file+'.html-list')

if __name__ == '__main__': sys.exit(main(sys.argv))
