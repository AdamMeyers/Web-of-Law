#!/usr/bin/env python3

from find_legislations import *
import sys
import os

def main (args):
    if len(args)<2:
        print('This function requires one argument: The name of a file -- the full path, but no extensions')
    else:
        base_file = args[1]
        if os.sep in base_file:
            sep_index = base_file.rindex(os.sep)
            file_id = base_file[sep_index:]
        else:
            file_id = base_file
        find_legislations(base_file+'.txt',file_id)

if __name__ == '__main__': sys.exit(main(sys.argv))
