import sys
import re

ALLTEXT = open(sys.argv[1]).read()
HEADER = open("FILE_HEADER.txt").read().strip()
m =  re.search("# #START_LICENSE.*# #END_LICENSE[^\n]+", ALLTEXT, re.DOTALL | re.MULTILINE)
if m:
    if m.group() != HEADER:
        NEWFILE = ALLTEXT.replace(m.group(), HEADER+"\n")
        print sys.argv[1], "LICENSE CHANGED"
        open(sys.argv[1], "w").write(NEWFILE)
else:
    NEWFILE =  HEADER +"\n"+ ALLTEXT
    print sys.argv[1], "LICENSE ADDED"
    open(sys.argv[1], "w").write(NEWFILE)
