#####################
Installing a homu bot
#####################

This page has some more detailed explanations arising from following the `homu
installation instructions <https://github.com/barosl/homu>`_.

The page at http://homu.io describes a hosted homu service with some
background on the homu command.

Here I'm describing the procedure for running another homu service on
``nipy.bic.berkeley.edu``.

**********************************
Create github account for homu bot
**********************************

Created new Github account ``nibotmi``.

The github `terms of service
<https://help.github.com/articles/github-terms-of-service>`_ only allow one
free account but I contacted Github support, and they told me that "When needed
for legitimate purposes, we can allow users up to one (1) extra account as
a "machine" account for automation needs."

Although the `homu installation instructions`_ point out you can use an
existing user, the homu code specifically checks if the logged-in github user
from a particular pull request is the same as the homu user, so you shouldn't
use your normal github login user as the homu user.

***************************
Register github application
***************************

As homu user (``nibotmi``) went to: https://github.com/settings/developers

Registered a new application called ``mb-homu``.

* Homepage URL: http://nipy.bic.berkeley.edu:54856/
* Authorization callback URL: http://nipy.bic.berkeley.edu:54856/callback

Note Client ID and Client Secret for ``cfg.toml`` file on
``nipy.bic.berkeley.edu``.

**************************
Make personal access token
**************************

Went to: https://github.com/settings/tokens

New token named ``mb-homu``.

Permissions: ``repo``.

Noted token string.

**********************************
Add webhook for participating repo
**********************************

I'm configuring for my ``transforms3d`` repo.

Went to: https://github.com/matthew-brett/transforms3d/settings/hooks

Add webhook.

* Payload URL: http://nipy.bic.berkeley.edu:54856/github
* Content type: application/json
* Secret generated with ``openssl rand -hex 20`` as suggested in
  ``cfg.sample.toml``;
* "Let me select individual events", select "Pull request", "Push", "Issue
  comment";

*********************
Add webhook to github
*********************

Edits suggested to ``.travis.yml``::

    notifications:
        webhooks: http://nipy.bic.berkeley.edu:54856/travis

    branches:
        only:
            - auto

********
Firewall
********

We're running CentOS 7 on nipy.bic.berkeley.edu.

From `this SO answer
<http://stackoverflow.com/questions/24729024/centos-7-open-firewall-port>`_ and
the `Fedora wiki <https://fedoraproject.org/wiki/FirewallD>`_ I ran commands::

    firewall-cmd --zone=public --add-port=54856/tcp --permanent
    firewall-cmd --reload

Check this worked with::

    firewall-cmd --list-all

I checked the port before and after with ``telnet nipy.bic.berkeley.edu
54856`` from another machine.

**********************************
Running homu as daemon via systemd
**********************************

File ``/home/homu/bin/start-homu``::

    #!/bin/bash
    cd $HOME/homu
    source bin/activate
    homu

File ``/usr/lib/systemd/system/homu.service`` (see:
http://www.redmine.org/boards/1/topics/32763)::

    [Unit]
    Description=Homu daemon
    After=syslog.target
    After=network.target

    [Service]
    Type=simple
    User=homu
    Group=homu
    ExecStart=/home/homu/bin/start-homu

    # Give a reasonable amount of time for the server to start up/shut down
    TimeoutSec=300

    [Install]
    WantedBy=multi-user.target

Then, as sudo::

    systemctl enable homu.service
    systemctl start homu.service

To check how things are going::

    systemctl status homu.service

To check whether something is responding on the relevant port::

    telnet nipy.bic.berkeley.edu 54856

on another machine.

I had previously tried running this as a `user systemd
<https://wiki.archlinux.org/index.php/Systemd/User>`_ service but ran into
trouble configuring the startup, with DBus errors trying to enable or start the
service.

**********
Using homu
**********

The homu command starts a webserver that listens on the homu port, and returns
some details of what it's up to, as well as a cheat sheet of valid commands:
http://nipy.bic.berkeley.edu:54856
