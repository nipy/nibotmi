user { 'buildbot':
    ensure     => present,
               home       => '/home/buildbot',
               managehome => true,
}
