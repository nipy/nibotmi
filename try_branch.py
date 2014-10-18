#!/usr/bin/env python
""" Push code from a branch for testing on the nipy buildbots

You will need ssh access to the buildbot machine.

Use with something like::

    cd ~/repos/dipy
    git checkout my-interesting-branch
    try_branch.py dipy-py2.7-win32

"""
from __future__ import print_function

from subprocess import check_output
from argparse import ArgumentParser, RawDescriptionHelpFormatter
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
import re

SSH_RE = re.compile(r'(\w+)@(.*):(\w+)/(\w+)')

BUILDBOT_HOST = 'nipy.bic.berkeley.edu'
BUILDBOT_USER = 'buildbot'
BUILDBOT_JOBDIR = '~buildbot/nibotmi/jobdir'


def get_parser():
    parser = ArgumentParser(
        description=
"Push code from current branch for testing on nipy buildbots",
        epilog=
""" Push code from current branch to buildbot for testing

* Work out upstream remote
* Fetch upstream remote in order to fetch <upstream>/master
* Calculate diff against <upstream>/master
* Push diff to buildbot via ssh
""",
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('builder_names', type=str, help='name of builder',
                       nargs='+')
    parser.add_argument('--host', type=str, help='URL of buildbot host',
                        default=BUILDBOT_HOST)
    parser.add_argument('--user', type=str, help='username on buildbot host',
                        default=BUILDBOT_USER)
    parser.add_argument('--jobdir', type=str, help='jobdir on buildbot host',
                        default=BUILDBOT_JOBDIR)
    parser.add_argument('--branch', type=str, help='upstream branch name',
                        default='master')
    parser.add_argument('--patch-filename', type=str,
                        help='written patch filename',
                        default='.buildbot.patch')
    parser.add_argument('--git-org', type=str,
                        help='organization containing git repo',
                        default='nipy')

    return parser


def bt(cmd):
    return check_output(cmd).decode('latin1').strip()


def find_upstream(git_org, git_host='github.com'):
    """ Find remote that is probably upstream

    Return name, ``git://`` form of URL of repo, or raise error if not found
    """
    for remote in bt(['git', 'remote', '-v']).splitlines():
        name, url, type = remote.strip().split()
        if not type == '(fetch)':
            continue
        match = SSH_RE.match(url)
        if not match is None:
            user, host, org, repo = match.groups()
            if (host, org) == (git_host, git_org):
                return name, 'git://{host}/{org}/{repo}.git'.format(
                    host=host, org=org, repo=repo)
            continue
        parsed = urlparse(url)
        if not parsed.netloc == git_host:
            continue
        null, org, repo = parsed.path.split('/', 2)
        if org == git_org:
            if not repo.endswith('.git'):
                repo += '.git'
            return name, 'git://{host}/{org}/{repo}'.format(
                    host=parsed.netloc, org=org, repo=repo)
    raise RuntimeError("Cannot find upstream remote")


def main():
    # parse the command line
    parser = get_parser()
    args = parser.parse_args()
    upstream, git_url = find_upstream(args.git_org)
    bt(['git', 'fetch', upstream])
    diff = check_output(['git', 'diff', '--binary',
                         '{0}/{1}..'.format(
                             upstream, args.branch)])
    with open(args.patch_filename, 'wb') as fobj:
        fobj.write(diff)
    print(bt(['buildbot', 'try',
              '--diff=' + args.patch_filename,
              '--patchlevel=1',
              '--connect=ssh',
              '--username=' + args.user,
              '--host=' + args.host,
              '--jobdir=' + args.jobdir,
              '--repository=' + git_url,
              '--branch=' + args.branch] +
             ['--builder=' + builder for builder in args.builder_names]))


if __name__ == '__main__':
    main()
