#!/usr/bin/python env
# script that reads two files in utf-8 format
# and prints them out when two lines are the same (not translated)
import codecs
import sys

with codecs.open(sys.argv[3],'w',encoding='utf8') as out:
    with codecs.open(sys.argv[1],'r',encoding='utf8') as arch1:
            counter = 0
            for line1 in arch1:
                counter2=0
                with codecs.open(sys.argv[2],'r',encoding='utf-8') as arch2:
                    for line2 in arch2:
                        if(counter==counter2):
                            if(line1.strip()==line2.strip()):
                                out.write(line1.strip()) 
                                out.write('\n') 
                        counter2+=1
                arch2.close()
                counter+=1
            arch1.close()
