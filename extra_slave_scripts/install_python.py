#!/usr/bin/env python
""" Install Python and Pip and Nose and Virtualenv from upstream installers
"""
from __future__ import print_function, division

import os
import sys
from os.path import join as pjoin, dirname, exists
from subprocess import Popen, PIPE, check_call
from urllib import urlretrieve

DOWNLOAD_PATH='/Users/Shared/Downloads'
PYTHON_DMG_URL= 'https://www.python.org/ftp/python'
GET_PIP_URL = 'https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py'
PY_DMG_MOUNT = '/Volumes/Python'
POPY_BASE = '/Library/Frameworks/Python.framework/Versions'


def short_version(py_version):
    """ Return major.minor version from major.minor.point version

    >>> short_version('2.7.6')
    '2.7'
    """
    return '.'.join(py_version.split('.')[:2])


def get_version(py_bin):
    """ Return major.minor.point version from python executable `py_bin`

    `py_bin` should be on the system path.

    >>> get_version('/usr/bin/python')
    '2.6.1'
    """
    proc = Popen([py_bin, '--version'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    # Python 3 puts version into stdout
    out = stdout if len(stdout) > len(stderr) else stderr
    py, ver = out.decode('latin-1').strip().split()
    assert py == 'Python'
    return ver


def path_from_url(filename, url, always_download=False):
    """ Download file `filename` from URL `url`

    If `always_download` is False, and the filename exists in the global
    download directory, return existing file path, don't download.

    Otherwise download from given URL and return.
    """
    file_path = pjoin(DOWNLOAD_PATH, filename)
    if always_download or not exists(file_path):
        urlretrieve(url, file_path)
    return file_path


def install_python_org(py_version):
    """ Install given `py_version` of Python from Python.org installer

    Return path to Python binary
    """
    py_dmg='python-{0}-macosx10.6.dmg'.format(py_version)
    py_dmg_url = '{0}/{1}/{2}'.format(PYTHON_DMG_URL, py_version, py_dmg)
    py_dmg_path = path_from_url(py_dmg, py_dmg_url)
    check_call(['hdiutil', 'attach', py_dmg_path, '-mountpoint', PY_DMG_MOUNT])
    check_call(['sudo', 'installer', '-pkg',
                pjoin(PY_DMG_MOUNT, 'Python.mpkg'), '-target', '/'])
    check_call(['diskutil', 'unmount', PY_DMG_MOUNT])
    pyv = short_version(py_version)
    return '{0}/{1}/bin/python{1}'.format(POPY_BASE, pyv)


def install_pip(py_bin):
    """ Install pip corresponding to Python binary `py_bin`

    Return path to pip binary
    """
    get_pip = path_from_url('get-pip.py', GET_PIP_URL, always_download=True)
    check_call([py_bin, get_pip])
    pip_dir = dirname(py_bin)
    ver = get_version(py_bin)
    pip_bin = pjoin(pip_dir, 'pip' + short_version(ver))
    assert exists(pip_bin)
    return pip_bin


def link_force(src, dst):
    """ Hard link `src` file to path `dst`, deleting `dst` if it exists
    """
    if exists(dst):
        os.unlink(dst)
    os.link(src, dst)


def main():
    try:
        py_version = sys.argv[1]
    except IndexError:
        raise RuntimeError('Need Python full version string - e.g 2.7.6')
    # Wipe out all prior Python installations
    check_call(['ul-git-only'])
    # Install python and some packages
    py_bin = install_python_org(py_version)
    pip_bin = install_pip(py_bin)
    check_call([pip_bin, 'install', 'virtualenv'])
    link_force(py_bin, '/usr/local/bin/python')
    link_force(pip_bin, '/usr/local/bin/pip')
    bin_dir = dirname(py_bin)
    link_force(pjoin(bin_dir, 'virtualenv'), '/usr/local/bin/virtualenv')


if __name__ == '__main__':
    main()
