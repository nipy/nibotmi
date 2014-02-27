Create Buildbot master account
==============================

Create buildbot user account
----------------------------

Password is disabled by default in Fedora/Red Hat/CentOS.

::

  useradd buildbot

Put in public ssh key for own account and host buildbot account.

Note that Centos5 seems to require .ssh/authorized_keys chmod go-rwx.

::

  su - buildbot
  mkdir .ssh
  chmod go-rwx .ssh

scp your key to .ssh/authorized_keys

::

  chmod go-rwx .ssh/authorized_keys

Install buildbot locally
------------------------

::

  easy_install --prefix=~/.local -U buildbot

Add path in ``.bashrc``::

  # User specific aliases and functions

  pathmunge () {
      case ":${PATH}:" in
          *:"$1":*)
              ;;
          *)
              if [ "$2" = "after" ] ; then
                  PATH=$PATH:$1
              else
                  PATH=$1:$PATH
              fi
      esac
  }

  pathmunge ~/.local/bin

  export PATH
  unset pathmunge

Install buildmaster
-------------------

Checkout buildmaster from github::

  git clone https://github.com/nipy/nibotmi

Configure some gitpollers and schedulers as you see in the ``master.cfg`` file.
See also
http://onemanandafewelectrons.blogspot.com/2011/06/oh-wonderfull-build-bot.html

Create buildbot service
-----------------------

Create ``/etc/init.d/buildbot`` with the following content::

  #!/bin/sh
  #
  # chkconfig: 345 95 15
  # description: Starts and stops a buildbot master

  PROJECT="nibotmi"
  BB_USER="buildbot"
  MASTERS_DIR="/home/buildbot"
  BASE_DIR="${MASTERS_DIR}/${PROJECT}"
  BUILDBOT="/home/buildbot/.local/bin/buildbot"

  # Check that master.cfg exists.
  [ -f "${BASE_DIR}/master.cfg" ] || exit $?

  RETVAL=0

  start() {
  	printf "Starting buildbot master for %s\n" "$PROJECT"
          ACTION=start
          /bin/su $BB_USER -c "$BUILDBOT $ACTION $BASE_DIR"
  	RETVAL=$?
  	return $RETVAL
  }

  stop() {
  	printf "Stopping buildbot master for %s\n" "$PROJECT"
          ACTION=stop
          /bin/su $BB_USER -c "$BUILDBOT $ACTION $BASE_DIR"
  	RETVAL=$?
  	return $RETVAL
  }

  restart() {
          stop
          start
  }	
  
  reload() {
          printf "Reconfiguring build master for %s\n" "$PROJECT"
          ACTION=reconfig
          /bin/su $BB_USER -c "$BUILDBOT $ACTION $BASE_DIR"
  	RETVAL=$?
  	return $RETVAL
  }	
  
  case "$1" in
    start)
    	start
  	;;
    stop)
    	stop
  	;;
    restart)
    	restart
  	;;
    reload)
    	reload
  	;;
    *)
  	echo $"Usage: $0 {start|stop|restart|reload}"
  	exit 1
  esac
  
  exit $?

Enable it::

  chkconfig --add buildbot

Enable public website
---------------------

Install mod_proxy::

  yum install mod_proxy_html

Add buildbot proxy conf in ``/etc/httpd/conf.d/buildbot.conf``::

  ProxyPass / http://localhost:8010/
  ProxyPassReverse / http://localhost:8010/

Enable Apache::

  chkconfig httpd on
  service httpd start

Open port 80 by adding the following to ``/etc/sysconfig/iptables``::

  -A INPUT -m state --state NEW -m tcp -p tcp --dport 80 -j ACCEPT

Setting up a buildslave
-----------------------

On master:

Add buildslave name and password (below) to ``nipybuildbot.py`` and::

    cd nibotmi
    buildbot reconfig

In this case on Debian / Ubuntu::

    SLAVE_USER=buildslave
    SLAVE_NAME=my_slave
    SLAVE_PASSWORD=some-password-not-this-one
    PY_VER=python2.6

    sudo useradd -m $SLAVE_USER
    sudo passwd $SLAVE_USER
    # You'll need python and git and nosetests on the path
    sudo apt-get install git python-dev python-numpy python-nose python-setuptools
    su - $SLAVE_USER
    pip install --user buildbot-slave
    # Tests need virtualenv
    pip install --user virtualenv
    # Create build slave
    $HOME/.local/bin/buildslave create-slave $HOME/$SLAVE_NAME nipy.bic.berkeley.edu $SLAVE_NAME $SLAVE_PASSWORD
    # At this point you may want to edit the `admin` and `host` files in $HOME/$SLAVE_NAME/info
    # Start up build slave
    $HOME/.local/bin/buildslave start $HOME/$SLAVE_NAME
    # Make sure slave starts on reboot
    echo "@reboot $HOME/.local/bin/buildslave start $HOME/$SLAVE_NAME" > crontab.txt
    crontab crontab.txt

For any nipy build you'll need numpy on the python path seen by the buildslave.
For nipy tests, you'll also need scipy on your python path.  I tend to install
numpy and scipy systemwide.

For OSX - instructions are similar.  You will need to run the buildslave via
launchd - see http://trac.buildbot.net/wiki/UsingLaunchd  This involves making
a ``.plist`` file, putting it into ``/Library/LaunchDaemons``, setting user and
group to be ``root:wheel``, and either rebooting, or running `launchctl load
<plist file>` to start the daemon.  See the example ``.plist`` files in this
directory.  If you don't do this, and just run ``buildslave``, then the builds
will tend to die with DNS errors.

Giving yourself permission to trigger builds
--------------------------------------------

Ask for ssh access to the buildbot master account.

ssh into that account.

Then::

    cd nibotmi
    htpasswd -d bot_htpasswd your_chosen_username

Test that you can trigger builds using this username and password on the web
interface.

Let me (Matthew) know if you do this, so I can keep a backup of that
``bot_htpasswd`` file somewhere.

Please let us know if you have any problems.

Setting up wheelhouses on the slaves
------------------------------------

You may want to build dependencies locally on the buildslaves, so dependencies
can be more quickly installed for tests.

To do this, ssh into your buildslave account and:

* Make a directory to contain your wheels::

    mkdir ~/wheelhouse

* Make a virtualenv to build wheels in::

    virtualenv wheel-builder

* Activate the virtualenv
    . wheel-builder/bin/activate

* Upgrade virtualenv to latest pip, setuptools, add wheel package

    pip install -U setuptools
    easy_install -U pip
    pip install wheel

* Build your wheels::

    pip wheel --wheel-dir=/Users/buildslave/wheelhouse sympy cython

Then make a file ``~/.pip/pip.conf`` with contents::

    [global]
    find-links =
        /Users/buildslave/wheelhouse
    use-wheel = True

where ``/Users/buildslave/wheelhouse`` is the full path to your wheelhouse
directory.

After that, you should see builders on that slave pick up the wheels for their
dependencies, as long as you have compiled the right versions for the right
pythons.

If you are testing on more than one Python version, and your wheels are specific
to python versions, then make a virtualenv corresponding to all your python
versions::

  cd ~
  virtualenv --python=python3.3 wheel-builder-3.3
  . wheel-builder-3.3/bin/activate
  easy_install -U pip
  pip install -U setuptools
  pip install wheel
  pip wheel --wheel-dir=/Users/buildslave/wheelhouse sympy cython

and so on.

.. vim: ft=rst
