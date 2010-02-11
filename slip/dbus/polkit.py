# -*- coding: utf-8 -*-

# slip.dbus.polkit -- convenience decorators and functions for using PolicyKit
# with dbus services and clients
#
# Copyright © 2008, 2009 Red Hat, Inc.
# Authors: Nils Philippsen <nils@redhat.com>
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

"""This module contains convenience decorators and functions for using
PolicyKit with dbus services and clients."""

import os
import dbus
import dbus.mainloop.glib
import mainloop

__all__ = ["require_auth", "enable_proxy", "NotAuthorizedException",
           "IsSystemBusNameAuthorized"]


def require_auth(polkit_auth):

    def require_auth_decorator(method):
        assert hasattr(method, "_dbus_is_method")

        setattr(method, "_slip_polkit_auth_required", polkit_auth)
        return method

    return require_auth_decorator


EXC_NAME = "org.fedoraproject.slip.dbus.service.PolKit.NotAuthorizedException"


def enable_proxy(func):
    if PolKit.polkit_version() == "0":

        def enable_proxy_wrapper(*p, **k):
            auth_interface = PolKit._polkit_auth_interface()
            retval = None

            try:
                return func(*p, **k)
            except dbus.DBusException, e:
                exc_name = e.get_dbus_name()

                action_id = exc_name[len(EXC_NAME) + 1:]
                obtained = auth_interface.ObtainAuthorization(action_id,
                        dbus.UInt32(0), dbus.UInt32(os.getpid()))
                if not obtained:
                    raise
            else:
                raise

            return func(*p, **k)

        return enable_proxy_wrapper
    else:
        return func


class NotAuthorizedException(dbus.DBusException):

    _dbus_error_name = \
        "org.fedoraproject.slip.dbus.service.PolKit.NotAuthorizedException"

    def __init__(self, action_id, *p, **k):

        self._dbus_error_name = self.__class__._dbus_error_name + "."\
             + action_id
        super(NotAuthorizedException, self).__init__(*p, **k)


class VersionError(Exception):

    pass


class PolKit(object):

    polkit_valid_versions = ["1", "0"]
    __polkit_version = None
    __polkit_auth_interface = None
    __polkitd_interface = None
    __systembus = None
    __sessionbus = None
    __systembus_name = None

    @classmethod
    def __determine_polkit_version(cls):
        if not PolKit.__systembus:
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            PolKit.__systembus = dbus.SystemBus()

        if not PolKit.__polkit_version:
            pk_ver_objnamepathif = {"0": ("org.freedesktop.PolicyKit",
                                    "/",
                                    "org.freedesktop.PolicyKit"),
                                    "1": ("org.freedesktop.PolicyKit1",
                                    "/org/freedesktop/PolicyKit1/Authority",
                                    "org.freedesktop.PolicyKit1.Authority")}

            pk_ver_if = {}

            for (pkver, pkobjnamepathif) in pk_ver_objnamepathif.iteritems():
                (name, path, interface) = pkobjnamepathif
                try:
                    pk_ver_if[pkver] = \
                        dbus.Interface(PolKit.__systembus.get_object(name,
                                       path), interface)
                except dbus.DBusException:
                    pass

            if "1" in PolKit.polkit_valid_versions and "1" in pk_ver_if:
                PolKit.__polkit_version = "1"
                PolKit.__polkit_auth_interface = None
                PolKit.__polkitd_interface = pk_ver_if["1"]
            elif "0" in PolKit.polkit_valid_versions and "0" in pk_ver_if:
                PolKit.__polkit_version = "0"
                if not PolKit.__sessionbus:
                    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
                    PolKit.__sessionbus = dbus.SessionBus()
                authobj = \
                    PolKit.__sessionbus.get_object("org.freedesktop.PolicyKit.AuthenticationAgent"
                        , "/")
                PolKit.__polkit_auth_interface = dbus.Interface(authobj,
                        "org.freedesktop.PolicyKit.AuthenticationAgent")
                PolKit.__polkitd_interface = pk_ver_if["0"]
            else:
                raise VersionError("Cannot determine valid PolicyKit version.")

    @classmethod
    def polkit_version(cls):
        if not PolKit.__polkit_version:
            PolKit.__determine_polkit_version()
        return PolKit.__polkit_version

    @classmethod
    def _polkit_auth_interface(cls):
        if not PolKit.__polkit_version:
            PolKit.__determine_polkit_version()
        return PolKit.__polkit_auth_interface

    @classmethod
    def _polkitd_interface(cls):
        if not PolKit.__polkit_version:
            PolKit.__determine_polkit_version()
        return PolKit.__polkitd_interface

    @property
    def _systembus(self):
        if not hasattr(PolKit, "__systembus"):
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            PolKit.__systembus = dbus.SystemBus()
        return PolKit.__systembus

    def __list_obtainable_authorizations_0(self):
        if self.polkit_version() != "0":
            return None

        # already obtained authorizations

        f = os.popen("/usr/bin/polkit-auth")
        auths = map(lambda x: x.strip(), f.readlines())
        f.close()

        # not yet obtained authorizations

        f = os.popen("/usr/bin/polkit-auth --show-obtainable")
        auths.extend(map(lambda x: x.strip(), f.readlines()))
        f.close()

        return auths

    def __authorization_is_obtainable_1(self, authorization):
        pki = self._polkitd_interface()
        if not pki:
            return False

        if not self.__systembus_name:
            self.__systembus_name = self.__systembus.get_unique_name()

        (is_authorized, is_challenge, details) = \
            pki.CheckAuthorization(("system-bus-name",
                                    {"name": self.__systembus_name}),
                                   authorization, {}, 0, "")

        return is_authorized or is_challenge

    @classmethod
    def _no_or_long_timeout(cls):
        if not hasattr(cls, "__no_or_long_timeout"):
            if dbus.version < (0, 84, 0):
                import gobject

                # dbus-python uses seconds and the C library milliseconds

                cls.__no_or_long_timeout = gobject.G_MAXINT / 1000.0
            else:

                # timeout == None shall mean no timeout

                cls.__no_or_long_timeout = None
            return cls.__no_or_long_timeout

    def AreAuthorizationsObtainable(self, authorizations):
        if not self._polkitd_interface():
            return False

        if isinstance(authorizations, basestring):
            authorizations = [authorizations]

        if self.polkit_version() == "1":
            obtainable = \
                reduce(lambda x, y: x and \
                                    self.__authorization_is_obtainable_1(y),
                       authorizations, True)

            return obtainable
        elif self.polkit_version() == "0":
            all_auths = self.__list_obtainable_authorizations_0()

            obtainable = reduce(lambda x, y: x and y in all_auths,
                                authorizations, True)

            return obtainable
        else:
            return False

    def IsSystemBusNameAuthorized(self, system_bus_name, action_id,
        challenge=True, details={}):
        """Don't call this inside a D-Bus method or signal handler."""

        import warnings
        warnings.warn("This method is not safe to use in all circumstances. Use IsSystemBusNameAuthorizedAsync() instead.", DeprecationWarning, stacklevel=2)

        ml = mainloop.MainLoop()

        reply = {}

        def reply_cb(is_auth):
            reply["reply"] = is_auth
            ml.quit()

        def error_cb(error):
            reply["error"] = error
            ml.quit()

        self.IsSystemBusNameAuthorizedAsync(system_bus_name, action_id,
            reply_handler=reply_cb, error_handler=error_cb,
            challenge=challenge, details=details)

        ml.run()

        if "error" in reply:
            raise reply["error"]

        return reply["reply"]

    def IsSystemBusNameAuthorizedAsync(self, system_bus_name, action_id,
        reply_handler, error_handler, challenge=True, details={}):

        pkv = self.polkit_version()
        if pkv == "1":
            self.IsSystemBusNameAuthorizedAsync_1(system_bus_name, action_id,
                    reply_handler=reply_handler, error_handler=error_handler,
                    details=details)
        elif pkv == "0":
            self.IsSystemBusNameAuthorizedAsync_0(system_bus_name, action_id,
                    reply_handler=reply_handler, error_handler=error_handler)

    def IsSystemBusNameAuthorizedAsync_0(self, system_bus_name, action_id,
        reply_handler, error_handler):

        revoke_if_one_shot = True

        def reply_cb(args):
            reply_handler(args == "yes")

        self._polkitd_interface().IsSystemBusNameAuthorized(action_id,
            system_bus_name, revoke_if_one_shot,
            reply_handler=reply_cb, error_handler=error_handler,
            timeout=self._no_or_long_timeout())

    def IsSystemBusNameAuthorizedAsync_1(self, system_bus_name, action_id,
        reply_handler, error_handler,
        challenge=True, details={}):

        flags = 0
        if challenge:
            flags |= 0x1

        def reply_cb(args):
            (is_authorized, is_challenge, details) = args
            reply_handler(is_authorized)

        self._polkitd_interface().\
                CheckAuthorization(("system-bus-name",
                                    {"name": system_bus_name}),
                                   action_id, details, flags, "",
                                   reply_handler=reply_cb,
                                   error_handler=error_handler,
                                   timeout=self._no_or_long_timeout())


__polkit = PolKit()


def AreAuthorizationsObtainable(authorizations):
    return __polkit.AreAuthorizationsObtainable(authorizations)


def IsSystemBusNameAuthorized(system_bus_name, action_id, challenge=True,
    details={}):

    import warnings
    warnings.warn("This function is not safe to use in all circumstances. Use IsSystemBusNameAuthorizedAsync() instead.", DeprecationWarning, stacklevel=2)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return __polkit.IsSystemBusNameAuthorized(system_bus_name, action_id,
                challenge, details)


def IsSystemBusNameAuthorizedAsync(system_bus_name, action_id,
    reply_handler, error_handler, challenge=True, details={}):

    return __polkit.IsSystemBusNameAuthorizedAsync(system_bus_name, action_id,
        reply_handler, error_handler, challenge, details)


