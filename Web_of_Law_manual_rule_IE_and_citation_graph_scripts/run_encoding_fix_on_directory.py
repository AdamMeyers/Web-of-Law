#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## This script fixes some encoding errors created by improperly
## reading in some files. It does not correct the initial bug, but
## rather patches the output. Specifically, characters that were
## originally encoded as cp1252 were not converted properly to utf8.
## Also, some mdashes were replaced with utf8 character 151 (or hex
## 97), which is not printable.

import sys
from encoding_fix import *

def main (args):
    if len(args) <2:
        print('This function requires at least one or two arguments: An input directory and an output directory')
    else:
        decode_json_files_in_directory(args[1],args[2])

if __name__ == '__main__': sys.exit(main(sys.argv))

