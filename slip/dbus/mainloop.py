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

__all__ = ("MainLoop", "set_type")

_mainloop_class = None


class MainLoop(object):
    """An abstract main loop wrapper class and factory.

    Use MainLoop() to get a main loop wrapper object for a main loop type
    previously registered with set_type(). Defaults to glib main loops.

    Actual main loop wrapper classes are derived from this class."""

    def __new__(cls, *args, **kwargs):
        global _mainloop_class
        if _mainloop_class is None:
            set_type("glib")
        return super(MainLoop, cls).__new__(_mainloop_class, *args, **kwargs)

    def pending(self):
        """Returns if there are pending events."""

        raise NotImplementedError()

    def iterate(self):
        """Iterates over one pending event."""

        raise NotImplementedError()

    def iterate_over_pending_events(self):
        """Iterates over all pending events."""

        while self.pending():
            self.iterate()

    def run(self):
        """Runs the main loop."""

        raise NotImplementedError()

    def quit(self):
        """Quits the main loop."""

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
    """Set a main loop type for non-blocking interfaces.

    mltype: "glib" (currently only glib main loops are supported)"""

    global _mainloop_class

    if _mainloop_class is not None:
        raise RuntimeError("The main loop type can only be set once.")

    ml_type_class = {"glib": GlibMainLoop}

    if mltype in ml_type_class:
        _mainloop_class = ml_type_class[mltype]
    else:
        raise ValueError("'%s' is not one of the valid main loop types (%s)." %
                          (mltype, ",".join(ml_type_class.keys())))


