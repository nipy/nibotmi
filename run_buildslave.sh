#!/bin/sh
export PATH=/Library/Frameworks/Python.framework/Versions/2.7/bin:/bin:/usr/bin:/usr/sbin:/sbin:/usr/local/bin
/Users/buildslave/Library/Python/2.7/bin/twistd --nodaemon --python=buildbot.tac --logfile=buildbot.log --prefix=slave

