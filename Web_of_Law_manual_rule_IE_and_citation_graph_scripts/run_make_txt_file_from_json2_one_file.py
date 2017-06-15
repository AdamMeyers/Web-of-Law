#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## This script creates one txt and one offset file from a json file.
## You can call this with one or two arguments.
## The first argument should be the input json file.
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
        print('This function requires one argument: a json file')
    else:
        parse_out_txt_file2(args[1])

if __name__ == '__main__': sys.exit(main(sys.argv))
