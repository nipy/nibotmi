####################
Test rig for nibotmi
####################

::

    cd test-rig
    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt
    buildbot create-master master
    buildbot start master

Create a slave, which might have the same name as one of the real slaves in
the ``local_setup.py`` file.  In my case, I'm using my Mac laptop to emulate a
Mac desktop slave called ``osx-10.8``::

    buildslave create-slave slave localhost:9989 osx-10.8 pass
    buildslave start slave

You should now be able to see your buildbot instance on http://localhost:8010

To use the web form, log in with user ``user`` and password ``pass``.

To finish up::

    buildbot stop master
    buildslave stop slave
    deactivate
