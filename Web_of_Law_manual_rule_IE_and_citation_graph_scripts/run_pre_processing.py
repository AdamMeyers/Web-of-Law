#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys

from pre_process_annotation import *

## This script creates some files for use with Amber Stubbs' Mae annotation program.
## The input is a directory which contains appellate court cases in the Web of Law format
## The system finds sets of three corresponding files: .txt, .case8 and .quotes 
## and outputs a .xml file that can be used as input to Mae.

def main (args):
    directory = args[1]
    for infile in list(os.listdir(directory)):
        if (infile.endswith('.txt')):
            case8 = file_name_append(directory,infile[:-4]+'.case8')
            quotes = file_name_append(directory,infile[:-4]+'.quotes')
            outfile = file_name_append(directory,infile[:-4]+'_annotate.xml')
            infile = file_name_append(directory,infile)
            if os.path.isfile(case8) and os.path.isfile(quotes):
                pre_process_web_of_law_IE(infile,case8,quotes,outfile)

if __name__ == '__main__': sys.exit(main(sys.argv))
            
