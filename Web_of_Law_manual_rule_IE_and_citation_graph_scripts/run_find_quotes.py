#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This script runs through a directory and finds all the quoted text for each txt file,
# producing one ".quotes" file for each .txt file.

from find_quotes import *
import sys
import os

def main (args):
    for infile in list(os.listdir(args[1])):
        if infile.endswith('.txt'):
            outfile = file_name_append(args[1],infile[:-4]+'.quotes')
            infile2 = file_name_append(args[1],infile)
            find_quotes(infile2,outfile)
            
if __name__ == '__main__': sys.exit(main(sys.argv))
