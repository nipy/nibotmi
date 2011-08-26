# This is a puppet manifest,
# it is intended to be run as 'sudo puppet nipybuildbot' on a slave
# please change the lines after:
# exec {'nipy-slave':
# and after 
# file {'/home/buildbot/nipy-slave/info/admin':

#group {'buildout':
#    ensure => present,
#}

user { 'buildbot':
    ensure     => present,
#groups => 'buildout',
        shell => '/bin/bash',
        home       => '/home/buildbot',
        managehome => true,
#require => Group['buildout']
}


File{
    ensure => 'present',
        owner => 'buildbot',
        require => User['buildbot']
}

package { "buildbot": ensure => installed } # get buildbot from the system package manager

file { '/home/buildbot':
     ensure => directory,
     require => User['buildbot']
 }
file { '/home/buildbot/.buildout':
     ensure => directory,
     require => File['/home/buildbot']
 }


Exec {
    path => [
        '~/.local/bin',
        '/usr/local/bin',
        '/usr/bin',
        '/bin',
        ],
    user => 'buildbot',
    cwd =>'/home/buildbot',
    logoutput => true,
}

#exec { 'create .local':
#command => "local processor=$(uname -p)
#local PYVER=$(python -ESV 2>&1);
#local PYVER_MAJOR=$(echo ${PYVER:7:3})
#local pypath=python${PYVER_MAJOR}/site-packages
#if [[ $processor == 'x86_64' ]]; then
#    mkdir $HOME/.local/lib64/$pypath
#fi
#mkdir $HOME/.local/lib/$pypath
#echo $HOME/.local/lib/$pypath
#",
#creates => '/home/buildout/.local/lib',
#user=>'buildbot',
#require => User['buildbot']
#}

file { '/home/buildbot/.buildout/default.cfg':
    ensure => present,
        content=> "[buildout]
eggs-directory = /home/buildbot/.buildout/eggs
download-cache = /home/buildbot/.buildout/downloads
extends-cache = /home/buildbot/.buildout/configs
",
require => File["/home/buildbot/.buildout"]
}

file { '/home/buildbot/.buildout/eggs':
    ensure => directory}
file { '/home/buildbot/.buildout/downloads':
    ensure => directory}
file { '/home/buildbot/.buildout/configs':
    ensure => directory}

#exec {'buildbot-slave':
#command=>"easy_install --prefix=~/.local buildbot-slave",
#user=>'buildbot',
#creates=>'/home/buildbot/.local/bin/buildslave',
#logoutput => true,
#}

exec {'nipy-slave':
command=>'buildbot create-slave nipy-slave nipy.bic.berkeley.edu:9989 pi-ApxuMed bongo-builder',
creates => '/home/buildbot/nipy-slave',
require => Package['buildbot']
}

file { '/home/buildbot/set_info':
    content => "#!/bin/bash
cat /etc/issue > ~buildbot/nipy-slave/info/host
uname -a >> ~buildbot/nipy-slave/info/host
cat /proc/cpuinfo | grep -i 'model name' >> ~buildbot/nipy-slave/info/host
cat /proc/meminfo | grep -i MemTotal >> ~buildbot/nipy-slave/info/host
",
mode => 755,
require => [Exec['nipy-slave'], User['buildbot']]
}

file {'/home/buildbot/nipy-slave/info/admin':
        content=> "Paul Ivanov <pi.berkeley.edu>",
require => [Exec['nipy-slave'], User['buildbot']]
}

exec {'set_info':
command => '/home/buildbot/set_info',
#subscribe => File['/home/buildbot/set_info'],
require => [File['/home/buildbot/set_info'], Exec['nipy-slave'], User['buildbot']]
}

cron {'nipy buildbot':
    command => 'buildbot start /home/buildbot/nipy-slave',
    user => 'buildbot',
    special => 'reboot',
    require => User['buildbot']
}

exec {'start buildslave':
    command => 'buildbot restart /home/buildbot/nipy-slave ;', 
    user => 'buildbot',
    cwd => '/home/buildbot',
    require => [Exec['nipy-slave'],Exec['set_info'], File['/home/buildbot/nipy-slave/info/admin'],User['buildbot']],
}
