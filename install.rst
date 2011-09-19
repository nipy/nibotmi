Create Buildbot master account
==============================

Create buildbot user account
----------------------------

# Password is disabled by default in Fedora/Red Hat/CentOS.

::

  useradd buildbot

# Put in public ssh key for own account and host buildbot account.
# Note that Centos5 seems to require .ssh/authorized_keys chmod go-rwx.

::

  su - buildbot
  mkdir .ssh
  chmod go-rwx .ssh

# scp your key to .ssh/authorized_keys

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

  git clone http://github.com/...

Configure some gitpollers and schedulers as in
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

In this case on Ubuntu

* sudo useradd -m buildslave
* sudo passwd buildslave
* sudo apt-get install git python-dev python-numpy python-nose
* su - buildslave
* mkdir -p /home/buildslave/.local/lib/python2.6/site-packages
* easy_install --prefix=~/.local buildbot-slave
* /home/buildslave/.local/bin/buildslave create-slave /home/buildslave/slave-name nipy.bic.berkeley.edu slave-name slave-password
* Add buildslave name and password to ``nipybuildbot.py`` file on master.
* On master : ``buildbot reconfig``
* /home/buildslave/.local/bin/buildslave start /home/buildslave/slave-name
* ``echo "@reboot /home/buildslave/.local/bin/buildslave start /home/buildslave/slave-name" > crontab.txt``
* crontab crontab.txt
