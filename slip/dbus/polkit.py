# -*- coding: utf-8 -*-
# slip.dbus.polkit -- convenience functions for using PolicyKit with dbus
# services
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

"""This module contains convenience functions for using PolicyKit with dbus
services."""

import dbus

__all__ = ['auth_required', 'IsSystemBusNameAuthorized', 'IsProcessAuthorized']

class NotAuthorized (dbus.DBusException):
    _dbus_error_name = "org.fedoraproject.slip.dbus.service.PolKit.NotAuthorized"
    def __init__ (self, action_id, *p, **k):
        self._dbus_error_name = self.__class__._dbus_error_name + "." + action_id
        super (NotAuthorized, self).__init__ (*p, **k)

class PolKit (object):
    @property
    def _systembus (self):
        if not hasattr (PolKit, "__systembus"):
            PolKit.__systembus = dbus.SystemBus ()
        return PolKit.__systembus

    @property
    def _dbusobj (self):
        if not hasattr (PolKit, "__dbusobj"):
            PolKit.__dbusobj = self._systembus.get_object ("org.freedesktop.PolicyKit", "/")
        return PolKit.__dbusobj

    def IsSystemBusNameAuthorized (self, system_bus_name, action_id):
        revoke_if_one_shot = True
        return self._dbusobj.IsSystemBusNameAuthorized (action_id, system_bus_name, revoke_if_one_shot, dbus_interface = "org.freedesktop.PolicyKit")

    def IsProcessAuthorized (self, pid, action_id):
        revoke_if_one_shot = True
        return self._dbusobj.IsSystemBusNameAuthorized (action_id, pid, revoke_if_one_shot, dbus_interface = "org.freedesktop.PolicyKit")

__polkit = PolKit ()

def IsSystemBusNameAuthorized (system_bus_name, action_id):
    return __polkit.IsSystemBusNameAuthorized (system_bus_name, action_id)

def IsProcessAuthorized (pid, action_id):
    return __polkit.IsProcessAuthorized (pid, action_id)

def auth_required (polkit_auth):
    def polkit_auth_require (method):
        assert hasattr (method, "_dbus_is_method")

        setattr (method, "_slip_polkit_auth_required", polkit_auth)
        return method
    return polkit_auth_require
