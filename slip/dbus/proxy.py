# -*- coding: utf-8 -*-
# slip.dbus.service -- convenience functions for using dbus proxies
#
# Copyright © 2008 Red Hat, Inc.
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
# Authors: Nils Philippsen <nphilipp@redhat.com>

"""This module contains convenience functions for using dbus proxies."""

import dbus

__all__ = ["exception_defaults", "unknown_method_default"]

def exception_defaults (exceptions_values):
    """Returns a default value if a dbus method throws exceptions.

The exceptions_values parameter is a dict which maps exception names to the
values that should be returned if the dbus call throws this dbus exception.
None as the key means all exceptions which aren't handled specifically."""

    if not isinstance (exceptions_values, dict):
        raise TypeError ("exceptions_values must be a dictionary")
    for name in exceptions_values:
        if not isinstance (name, basestring) and name != None:
            raise TypeError ("keys of exceptions_values must be strings or None, not %s" % name)

    def exception_defaults_decorator (func):
        def exception_defaults_wrapper (*p, **k):
            try:
                return func (*p, **k)
            except dbus.DBusException, e:
                exc_name = e.get_dbus_name ()

                if exc_name in exceptions_values.keys ():
                    return exceptions_values[exc_name]
                elif None in exceptions_values.keys ():
                    return exceptions_values[None]
                else:
                    raise
        return exception_defaults_wrapper
    return exception_defaults_decorator

def unknown_method_default (default_value):
    """Returns default_value if the method is unknown to dbus, e.g. after a
previously existing object was deleted."""

    return exception_defaults ({"org.freedesktop.DBus.Error.UnknownMethod": default_value})
