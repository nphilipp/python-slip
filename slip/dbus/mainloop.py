# -*- coding: utf-8 -*-

# slip.dbus.mainloop -- mainloop wrappers
#
# Copyright © 2009 Red Hat, Inc.
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Authors:
# Nils Philippsen <nils@redhat.com>

"""This module contains mainloop wrappers."""

_mainloop_class = None


class MainLoop(object):

    def __new__(cls, *args, **kwargs):
        global _mainloop_class
        if _mainloop_class is None:
            set_type("glib")
        return super(MainLoop, cls).__new__(_mainloop_class, *args, **kwargs)

    def pending(self):
        raise NotImplementedError()

    def iterate(self):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    def quit(self):
        raise NotImplementedError()


class GlibMainLoop(MainLoop):

    def __init__(self):
        import gobject
        ml = gobject.MainLoop()
        ctx = ml.get_context()

        self._mainloop = ml
        self.pending = ctx.pending
        self.iterate = ctx.iteration
        self.run = ml.run
        self.quit = ml.quit


def set_type(mltype):
    global _mainloop_class

    if _mainloop_class is not None:
        raise RuntimeError("The main loop type can only be set once.")

    ml_type_class = {"glib": GlibMainLoop}

    if mltype in ml_type_class:
        _mainloop_class = ml_type_class[mltype]
    else:
        raise ValueError("'%s' is not one of the valid main loop types (%s)." %
                          (mltype, ",".join(ml_type_class.keys())))


