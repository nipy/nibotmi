#!/usr/bin/env python
""" Searches log for pattern

Example:

logsearch.py "*4-stdio.bz2" "command timed out"

Searches logs selected with glob.

Sorts logs by modification time.

For each log where pattern found, print 2 lines above and two lines below the
pattern for context.  Only find first pattern in each log
"""
from __future__ import print_function, division

import os
import sys
import re
import time
from glob import glob
import bz2


ABOVE_CONTEXT = 2
BELOW_CONTEXT = 2


def main():
    try:
        globber = sys.argv[1]
    except IndexError:
        raise RuntimeError("Need glob pattern to select logs")
    try:
        pattern = sys.argv[2]
    except IndexError:
        raise RuntimeError("Need pattern to search for in logs")
    filenames = glob(globber)
    pattern = re.compile(pattern)
    files_info = [(f, os.stat(f).st_mtime) for f in filenames]
    files_info.sort(key=lambda t : t[1])
    for fname, st_mtime in files_info:
        if fname.endswith('.bz2'):
            fobj = bz2.BZ2File(fname)
        else:
            fobj = open(fname, 'rt')
        lines = fobj.readlines()
        for i, line in enumerate(lines):
            if pattern.search(line):
                mod_time = time.gmtime(st_mtime)
                time_str = time.strftime("%m/%d/%Y %H:%M:%S", mod_time)
                print("{0} modified {1}".format(fname, time_str))
                first_i = max(0, i-ABOVE_CONTEXT)
                last_i = min(len(lines), i+ABOVE_CONTEXT)
                for j in range(first_i, last_i + 1):
                    print(lines[j].strip())
                break
        fobj.close()


if __name__ == '__main__':
    main()
