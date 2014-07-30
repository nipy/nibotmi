# local configuration for nipy buildbot

# master_url = "http://nipy.bic.berkeley.edu/"
master_url = "http://localhost:8010"
slave_port = 9989

# Passwords for buildslaves
# None of these slaves actually have 'pass' as a password; this is just a
# placeholder
slave_passes = {
    'tom-standard': 'pass',
    'osx-10.5-ppc': 'pass',
    'osx-mini': 'pass',
    'osx-10.6': 'pass',
    'osx-10.5': 'pass',
    'bongoslave': 'pass',
    'xp-standard': 'pass',
    'win7-32-mini': 'pass',
    'mike-win7-64': 'pass',
    'nd-bb-slave-sparc': 'pass',
    'nd-bb-slave-sparc-wheezy': 'pass',
    'nd-bb-slave-sparc-sid': 'pass',
    'pi-ykcyc': 'pass',
    'pi-pyanywhere': 'pass',
    'pi-ApxuMed': 'pass',
    'arm-raspberry-pi': 'pass',
    'debian-ppc-32': 'pass',
    'osx-10.7': 'pass',
    'osx-10.8': 'pass',
    'i20-fed19': 'pass',
    'osx-10.6-clean': 'pass',
}

# If you are trying to set up and test a real slave with a real password,
# consider making a file 'secret_passwords.py' with a 'slave_passes' dict
# containing the slave name(s) and password(s).  Don't commit it to version
# control though.
