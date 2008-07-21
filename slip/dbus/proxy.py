# -*- coding: utf-8 -*-
# slip.dbus.proxy -- convenience functions for using proxies for dbus services
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

"""This module contains convenience functions for using proxies of dbus
services."""

import os
import dbus

__all__ = ["polkit_enable"]

EXC_NAME = "org.fedoraproject.slip.dbus.service.PolKit.NotAuthorized"

def polkit_enable (func):
    def wrapper (*p, **k):
        sessionbus = None
        authobj = None
        retval = None

        try:
            return func (*p, **k)
        except dbus.DBusException, e:
            exc_name = e.get_dbus_name ()
            if exc_name.startswith (EXC_NAME + "."):
                if not sessionbus:
                    sessionbus = dbus.SessionBus ()
                    authobj = sessionbus.get_object ("org.freedesktop.PolicyKit.AuthenticationAgent", "/")

                action_id = exc_name[len (EXC_NAME)+1:]
                obtained = authobj.ObtainAuthorization (action_id, dbus.UInt32 (0),
                        dbus.UInt32 (os.getpid ()),
                        dbus_interface = "org.freedesktop.PolicyKit.AuthenticationAgent")
                if not obtained:
                    raise
            else:
                raise

        return func (*p, **k)
    return wrapper
