# -*- coding: utf-8 -*-

# slip._wrappers._glib -- abstract (some) differences between glib and
# gi.repository.GLib
#
# Copyright © 2012, 2015 Red Hat, Inc.
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

"""This module lets some other slip modules cooperate with either the glib
or the gi.repository.GLib modules."""

import sys

__all__ = ['MainLoop', 'source_remove', 'timeout_add']

_self = sys.modules[__name__]

_mod = None

while _mod is None:
    if 'gi.repository.GLib' in sys.modules:
        _mod = sys.modules['gi.repository.GLib']
    elif 'glib' in sys.modules:
        _mod = sys.modules['glib']
    # if not yet imported, try to import glib first, then
    # gi.repository.GLib ...
    if _mod is None:
        try:
            import glib
        except ImportError:
            import gi.repository.GLib
    # ... then repeat.

for what in __all__:
    if what not in dir(_self):
        setattr(_self, what, getattr(_mod, what))
