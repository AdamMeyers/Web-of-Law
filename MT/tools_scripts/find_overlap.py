#!/usr/bin/env python
# script to find the overlap between two files
import sys
file1 = []
with open(sys.argv[1], "r") as ins:
    for line in ins:
        file1.append(line.strip())
file2 = []
with open(sys.argv[2], "r") as ins:
    for line in ins:
        file2.append(line.strip())
for term in set(file1).intersection(file2):
    print term.strip()

