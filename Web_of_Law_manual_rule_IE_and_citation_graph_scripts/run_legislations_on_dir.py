#!/usr/bin/env python3

from find_legislations import *
import sys
import os

def main (args):
    if len(args)<2:
        print('This function requires one argument: The name of a directory -- the full path')
    else:
        base_dir = args[1]
        if base_dir.endswith(os.sep):
            base_dir = base_dir[:-1]
        for infile in list(os.listdir(base_dir)):
            if infile.endswith('.txt3'):
                file_id = infile[:-5]
                print(file_id)
                output = find_legislations(base_dir+os.sep+infile,file_id)
                outfile = base_dir+os.sep+file_id+'.legislation9'
                with open(outfile,'w') as outstream:
                    for line in output:
                        outstream.write(line+'\n')

if __name__ == '__main__': sys.exit(main(sys.argv))
