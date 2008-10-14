# -*- coding: utf-8 -*-
# slip.dbus.polkit -- convenience decorators and functions for using PolicyKit
# with dbus services and clients
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

"""This module contains convenience decorators and functions for using
PolicyKit with dbus services and clients."""

import os
import dbus

__all__ = ["require_auth", "enable_proxy", "NotAuthorizedException", "IsSystemBusNameAuthorized", "IsProcessAuthorized"]

def require_auth (polkit_auth):
    def require_auth_decorator (method):
        assert hasattr (method, "_dbus_is_method")

        setattr (method, "_slip_polkit_auth_required", polkit_auth)
        return method
    return require_auth_decorator

EXC_NAME = "org.fedoraproject.slip.dbus.service.PolKit.NotAuthorizedException"

def enable_proxy (func):
    def enable_proxy_wrapper (*p, **k):
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
    return enable_proxy_wrapper

class NotAuthorizedException (dbus.DBusException):
    _dbus_error_name = "org.fedoraproject.slip.dbus.service.PolKit.NotAuthorizedException"
    def __init__ (self, action_id, *p, **k):
        self._dbus_error_name = self.__class__._dbus_error_name + "." + action_id
        super (NotAuthorizedException, self).__init__ (*p, **k)

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

    def obtainable_authorizations (self):
        # already obtained authorizations
        f = os.popen ("/usr/bin/polkit-auth")
        auths = map (lambda x: x.strip (), f.readlines ())
        f.close ()
        # not yet obtained authorizations
        f = os.popen ("/usr/bin/polkit-auth --show-obtainable")
        auths.extend (map (lambda x: x.strip (), f.readlines ()))
        f.close ()

        return auths

    def AreAuthorizationsObtainable (self, authorizations):
        if isinstance (authorizations, basestring):
            authorizations = [authorizations]

        all_auths = self.obtainable_authorizations ()

        obtainable = reduce (lambda x, y: x and y in all_auths, authorizations, True)

        return obtainable

    def IsSystemBusNameAuthorized (self, system_bus_name, action_id):
        revoke_if_one_shot = True
        return self._dbusobj.IsSystemBusNameAuthorized (action_id, system_bus_name, revoke_if_one_shot, dbus_interface = "org.freedesktop.PolicyKit")

    def IsProcessAuthorized (self, pid, action_id):
        revoke_if_one_shot = True
        return self._dbusobj.IsSystemBusNameAuthorized (action_id, pid, revoke_if_one_shot, dbus_interface = "org.freedesktop.PolicyKit")

__polkit = PolKit ()

def AreAuthorizationsObtainable (authorizations):
    return __polkit.AreAuthorizationsObtainable (authorizations)

def IsSystemBusNameAuthorized (system_bus_name, action_id):
    return __polkit.IsSystemBusNameAuthorized (system_bus_name, action_id)

def IsProcessAuthorized (pid, action_id):
    return __polkit.IsProcessAuthorized (pid, action_id)
