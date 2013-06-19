#!/usr/bin/env python
""" Utilities for the buildslave """
import os
import sys
from glob import glob
from optparse import OptionParser


def path_prepend_str(search_dir):
    search_dir = os.path.abspath(search_dir)
    if os.path.sep == '/':
        print(search_dir + "/bin" + os.path.pathsep)
    elif os.path.sep == '\\':
        print(search_dir + "\\Scripts\\" + os.path.pathsep)
    else:
        raise RuntimeError("Oh dear, funny path sep")


def main():
    usage = """%prog [options] <command> <parameters>
where <command> can be:

path-prepend-str
abspath
pjoin
glob
"""
    parser = OptionParser(usage)
    opts, args = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(-1)
    command = args.pop(0)
    if command == 'path-prepend-str':
        path_prepend_str(*args)
    elif command == 'abspath':
        print(os.path.abspath(os.path.join(*args)))
    elif command == 'pjoin':
        print(os.path.join(*args))
    elif command == 'glob':
        globber = os.path.join(*args)
        print('\n'.join(sorted(glob(globber))))
    elif command == 'get-python-lib':
        from distutils.sysconfig import get_python_lib
        print(get_python_lib())
    else:
        parser.print_help()
        sys.exit(-1)


if __name__ == '__main__':
    main()
