#!/usr/bin/env python
import sys
if sys.platform == 'win32':
    print('.\\Scripts\\')
else:
    print('./bin/')
