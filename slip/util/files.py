# -*- coding: utf-8 -*-

#
# Copyright © 2009 Red Hat, Inc.
# Authors:
# Nils Philippsen <nils@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module contains helper functions for dealing with files."""

__all__ = ["issamefile", "linkfile", "copyfile", "linkorcopyfile"]

import os
import selinux
import shutil
import tempfile
import errno

BLOCKSIZE = 1024


def _issamefile(path1, path2):
    issame = False

    s1 = os.stat(path1)
    s2 = os.stat(path2)

    return os.path.samestat(s1, s2)


def issamefile(path1, path2, catch_stat_exceptions=[]):
    """Check whether two paths point to the same file (i.e. are hardlinked)."""

    if catch_stat_exceptions == True:
        catch_stat_exceptions = Exception

    try:
        return _issamefile(path1, path2)
    except catch_stat_exceptions:
        return False


def linkfile(srcpath, dstpath):
    """Hardlink srcpath to dstpath.

    Attempt to atomically replace dstpath if it exists."""

    if issamefile(srcpath, dstpath, catch_stat_exceptions=OSError):
        return

    dstpath = os.path.realpath(dstpath)
    dstdname = os.path.dirname(dstpath)
    dstbname = os.path.basename(dstpath)

    attempts = tempfile.TMP_MAX
    hardlinked = False
    while attempts > 0:
        attempts -= 1
        _tmpfilename = tempfile.mktemp(prefix=dstbname + ".", dir=dstdname)
        try:
            os.link(srcpath, _tmpfilename)
            hardlinked = True
            break
        except OSError, e:
            if e.errno == errno.EEXIST:

                # try another name

                pass
            else:
                raise e

    if hardlinked:
        os.rename(_tmpfilename, dstpath)


def copyfile(srcpath, dstpath, copy_mode_from_dst=True, run_restorecon=True):
    """Copy srcpath to dstpath.

    Abort operation if e.g. not enough space is available.  Attempt to
    atomically replace dstpath if it exists."""

    if issamefile(srcpath, dstpath, catch_stat_exceptions=OSError):
        return

    dstpath = os.path.realpath(dstpath)
    dstdname = os.path.dirname(dstpath)
    dstbname = os.path.basename(dstpath)

    srcfile = open(srcpath, "rb")
    dsttmpfile = tempfile.NamedTemporaryFile(prefix=dstbname + ".",
            dir=dstdname, delete=False)

    mode_copied = False

    if copy_mode_from_dst:

        # attempt to copy mode from destination file (if it exists,
        # otherwise fall back to copying it from the source file below)

        try:
            shutil.copymode(dstpath, dsttmpfile.name)
            mode_copied = True
        except (shutil.Error, OSError):
            pass

    if not mode_copied:
        shutil.copymode(srcpath, dsttmpfile.name)

    data = None

    while data != "":
        data = srcfile.read(BLOCKSIZE)
        try:
            dsttmpfile.write(data)
        except:
            srcfile.close()
            dsttmpfile.close()
            os.unlink(dsttmpfile.name)
            raise

    srcfile.close()
    dsttmpfile.close()

    os.rename(dsttmpfile.name, dstpath)

    if run_restorecon and selinux.is_selinux_enabled() > 0:
        selinux.restorecon(dstpath)


def linkorcopyfile(srcpath, dstpath, copy_mode_from_dst=True,
    run_restorecon=True):
    """First attempt to hardlink srcpath to dstpath, if hardlinking isn't
    possible, attempt copying srcpath to dstpath."""

    try:
        linkfile(srcpath, dstpath)
        return
    except OSError, e:
        if e.errno not in (errno.EMLINK, errno.EPERM, errno.EXDEV):

            # don't bother copying

            raise
        else:

            # try copying

            pass

    copyfile(srcpath, dstpath, copy_mode_from_dst, run_restorecon)


