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

from make_txt_file_from_json2 import *
import sys
import os

def main (args):
    if len(args)<2:
        print('This function requires one argument: A directory with json files')
    else:
        for infile in list(os.listdir(args[1])):
            if infile.endswith('.json'):
                parse_out_txt_file2(file_name_append(args[1],infile))

if __name__ == '__main__': sys.exit(main(sys.argv))
