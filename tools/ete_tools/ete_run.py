#!/usr/bin/env python
import sys
        
def main(argv):
    sys.argv = argv
    execfile(argv[0], globals())

if __name__ == '__main__':
    main(sys.argv[1:])
    
