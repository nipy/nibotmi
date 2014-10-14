#!/usr/bin/env python
""" Push code from a branch for testing on the nipy buildbots

You will need ssh access to the buildbot machine

Here's doing the code push long-hand::
    git diff main-master | buildbot try -p 1 --diff=- -c ssh -u buildbot -b
    dipy-py2.7-osx-10.8 --host=nipy.bic.berkeley.edu
    --jobdir=~buildbot/nibotmi/jobdir --branch=master
    --repository=git://github.com/nipy/dipy.git -p 1
"""
from __future__ import print_function

from subprocess import check_output, Popen, PIPE
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
* Fetch upstream remote to fetch upstream/master
* Calculate diff against upstream/master
* Push to buildbot via ssh
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
    return parser


def bt(cmd):
    return check_output(cmd).decode('latin1').strip()


def find_upstream(git_org='nipy', git_host='github.com'):
    """ Find remote that is probably upstream
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
    upstream, git_url = find_upstream()
    bt(['git', 'fetch', upstream])
    diff = check_output(['git', 'diff', '{0}/{1}..'.format(
        upstream, args.branch)])
    proc = Popen(['buildbot', 'try', '-p', '1', '--diff=-',
                  '-c', 'ssh',
                  '-u', args.user,
                  '--host', args.host,
                  '--jobdir=' + args.jobdir,
                  '--repository=' + git_url,
                  '--branch=' + args.branch] +
                 ['--builder=' + builder for builder in args.builder_names],
                 stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate(diff)
    print(stdout.decode('latin1'))
    if proc.returncode != 0:
        raise RuntimeError("buildbot try failed with error " +
                           stderr.decode('latin1'))


if __name__ == '__main__':
    main()
