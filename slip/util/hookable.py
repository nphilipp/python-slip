# -*- coding: utf-8 -*-
#
# Copyright © 2008 Red Hat, Inc.
# Authors:
# Nils Philippsen <nphilipp@redhat.com>
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

"""This module contains variants of certain base types which call registered
hooks on changes."""

def __wrap (func, methodname):
    def methodwrapper (self, *p, **k):
        retval = func (self, *p, **k)
        getattr (set, methodname)(self, *p, **k)
        self._run_hooks ()
        return retval
    return methodwrapper

class HookableSet (set):
    """A set object which calls registered hooks on changes."""

    def __init__ (self, *p, **k):
        super (HookableSet, self).__init__ (*p, **k)
        self.__hooks__ = set ()

    def add_hook (self, hook):
        assert callable (hook)
        self.__hooks__.add (hook)

    def remove_hook (self, hook):
        self.__hooks__.remove (hook)
    
    def _run_hooks (self):
        for hook in self.__hooks__:
            hook ()

    def copy (self):
        obj = set.copy (self)
        obj.__hooks__ = set ()
        return obj

for methodname in ("add", "clear", "difference_update", "discard",
        "intersection_update", "pop", "remove", "symmetric_difference_update",
        "update"):
    setattr (HookableSet, methodname, __wrap (getattr (set, methodname), methodname))
