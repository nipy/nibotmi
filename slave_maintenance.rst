###########################
Maintaining the buildslaves
###########################

Some notes on maintaining the build slaves

***
OSX
***

VNC access via command line
===========================

From:
http://superuser.com/questions/166179/how-to-enable-remote-access-for-another-account-on-mac-remotely-via-ssh/166188#166188

::

    sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -activate -configure -access -on -clientopts -setvnclegacy -vnclegacy yes -clientopts -setvncpw -vncpw mypasswd -restart -agent -privs -all

then::

    sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -deactivate -configure -access -off

Using VNC via safari in the browser:
http://www.davidtheexpert.com/post.php?id=5&question=The_very_best_VNC_client_for_Mac_OS_X_is_right_under_your_nose!

Good to be careful of VNC setting higher screen resolutions; this badly upset
the KVM I was using.  Resetting to 1024x768 seemed to calm it down.

Silverkeeper for bootable backup on 10.4: http://www.lacie.com/silverkeeper -
I needed a dedicated hard disk to make the bootable backup.

*******
Windows
*******

Windows backup, backed up to a shared SMB drive in OSX.

SSH access
==========

Cywgin ssh installed on both windows machines.

As I remember it, the defaults for ssh configuration worked fine.

Adding a user
=============

* Make user with Windows interface
* Make a password:
  http://www.howtogeek.com/howto/30184/10-ways-to-generate-a-random-password-from-the-command-line/
* Synchronize cygwin ``passwd`` with Windows::

    mkpasswd -cl > /etc/passwd
    mkgroup --local > /etc/group

  http://mig5.net/content/how-update-cygwin-etcpasswd-get-all-latest-windoze-users
* Do ``ssh newuser@localhost`` to check login
* As ``newuser``, record temporary password

On Windows 7
============

Starting up
-----------

Turn on file sharing via Control Panel, Network and Internet, Network and
Sharing center.

May or may not need to open Symantec Endpoint protection, Change Settings,
Network threat protection, Microsoft Windows Networking, enable / disable
browsing / sharing, Change advanced sharing settings (left of screen), turn on /
off file sharing.

For backup program, credentials for attaching to network drive, user has
to be preprended with host, as in "serverWithSambaDrive\usernameOnServer".

Needed a Samba settings change on Windows 7:
https://discussions.apple.com/message/6527267?messageID=6527267#6712693

    .. open up, secpol.msc (Local Security Policy) on your Windows machines.
    Navigate to Local Policies and then Security Options. Change Network
    security: LAN Manager authentication level to "Send NTLM response only".

Discussion of this setting here: http://technet.microsoft.com/en-us/library/jj852207(v=ws.10).aspx

When done
---------

Set back to default 'NTLMv2 responses only' after doing the backup.

Turn off file sharing / browsing in Control panel, Symantec Endpoint protection
as needed.

Windows XP
==========

Turn on / off network file browsing / sharing via Symantec Endpoint Protection
as above.

Restoring sounds like it will be painful: http://oreilly.com/pub/h/1196

