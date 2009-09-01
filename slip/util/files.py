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

__all__ = ["copyfile"]

import os
import selinux
import shutil
import tempfile

BLOCKSIZE = 1024

def copyfile (srcpath, dstpath, mode_from_dst = True, restorecon = True):
    dstpath = os.path.realpath (dstpath)
    dstdname = os.path.dirname (dstpath)
    dstbname = os.path.basename (dstpath)

    srcfile = open (srcpath, "rb")
    dsttmpfile = tempfile.NamedTemporaryFile (prefix = dstbname + ".",
            dir = dstdname, delete = False)

    mode_copied = False

    if mode_from_dst:
        # attempt to copy mode from destination file (if it exists,
        # otherwise fall back to copying it from the source file below)
        try:
            shutil.copymode (dstpath, dsttmpfile.name)
            mode_copied = True
        except shutil.Error:
            pass

    if not mode_copied:
        shutil.copymode (srcpath, dsttmpfile.name)

    data = None

    while data != "":
        data = srcfile.read (BLOCKSIZE)
        try:
            dsttmpfile.write (data)
        except IOError, ioe:
            srcfile.close ()
            dsttmpfile.close ()
            os.unlink (dsttmpfile.name)
            raise ioe

    srcfile.close ()
    dsttmpfile.close ()

    os.rename (dsttmpfile.name, dstpath)

    if restorecon and selinux.is_selinux_enabled () > 0:
        selinux.restorecon (dstpath)
