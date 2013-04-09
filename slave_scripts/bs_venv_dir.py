#!/usr/bin/env python
import os
import sys

search_dir = os.path.abspath(sys.argv[1])
if os.path.sep == '/':
    print(search_dir + "/bin/")
elif os.path.sep == '\\':
    print(search_dir + "\\Scripts\\")
else:
    raise RuntimeError("Oh dear, funny path sep")
