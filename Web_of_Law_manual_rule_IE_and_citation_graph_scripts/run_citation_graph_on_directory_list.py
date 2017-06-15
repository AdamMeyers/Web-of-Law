#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## This script creates a citation graph from a list of directories of
## files and also adds in global identifiers for citations into
## output files corresponding to each of the original opinions

import sys
import os
from coreference3 import *

def main (args):
    if len(args)<3:
        print('''This function requires two argument: 
    * The name of a file listing the directories containing input files
    * The prefix of the name of the output files''')
    directory_list = []
    with open(args[1]) as instream:
        for line in instream:
            line = line.strip(os.linesep)
            directory_list.append(line)
    run_global_coreference2(directory_list,args[2])

if __name__ == '__main__': sys.exit(main(sys.argv))
