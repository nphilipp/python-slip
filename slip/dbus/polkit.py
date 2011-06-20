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
from decorator import decorator

from constants import method_call_no_timeout

__all__ = ["require_auth", "enable_proxy", "AUTHFAIL_DONTCATCH",
           "NotAuthorizedException", "IsSystemBusNameAuthorized"]

def require_auth(polkit_auth):
    """Decorator for DBus service methods.

    Specify that a user needs a specific PolicyKit authorization `polkit_auth´
    to execute it."""

    def require_auth_decorator(method):
        assert hasattr(method, "_dbus_is_method")

        setattr(method, "_slip_polkit_auth_required", polkit_auth)
        return method

    return require_auth_decorator


AUTH_EXC_PREFIX = "org.fedoraproject.slip.dbus.service.PolKit.NotAuthorizedException."

class AUTHFAIL_DONTCATCH(object):
    pass

def enable_proxy(func=None, authfail_result=AUTHFAIL_DONTCATCH, authfail_exception=None, authfail_callback=None):
    """Decorator for DBus proxy methods.

    Let's you (optionally) specify either a result value or an exception type
    and a callback which is returned, thrown or called respectively if a
    PolicyKit authorization doesn't exist or can't be obtained in the DBus
    mechanism, i.e. an appropriate DBus exception is thrown.

    An exception constructor may and a callback must accept an `action_id´
    parameter which will be set to the id of the PolicyKit action for which
    authorization could not be obtained.

    You must decorate DBus proxy methods with enable_proxy if you want to use
    it with legacy PolicyKit versions (i.e. older than 0.9).

    Examples:

    1) Decorate a proxy method for use with PolicyKit < 0.9:

        class MyProxy(object):
            @polkit.enable_proxy
            def some_method(self, ...):
                ...

    2) Return `False´ in the event of an authorization problem, and call
    `error_handler´:

        def error_handler(action_id=None):
            print "Authorization problem:", action_id

        class MyProxy(object):
            @polkit.enable_proxy(authfail_result=False,
                                 authfail_callback=error_handler)
            def some_method(self, ...):
                ...

    3) Throw a `MyAuthError´ instance in the event of an authorization problem:

        class MyAuthError(Exception):
            def __init__(self, *args, **kwargs):
                action_id = kwargs.pop("action_id")
                super(MyAuthError, self).__init__(*args, **kwargs)
                self.action_id = action_id

        class MyProxy(object):
            @polkit.enable_proxy(authfail_exception=MyAuthError)
            def some_method(self, ...):
                ..."""

    assert(func is None or callable(func))

    assert(authfail_result in (None, AUTHFAIL_DONTCATCH) or authfail_exception is None)
    assert(authfail_callback is None or callable(authfail_callback))
    assert(authfail_exception is None or issubclass(authfail_exception, Exception))

    def _enable_proxy(func, *p, **k):
        pkver = PolKit.polkit_version()

        def handle_authfail(e):
            assert isinstance(e, dbus.DBusException)

            exc_name = e.get_dbus_name()

            if not exc_name.startswith(AUTH_EXC_PREFIX):
                raise e

            action_id = exc_name[len(AUTH_EXC_PREFIX):]

            if authfail_callback is not None:
                authfail_callback(action_id=action_id)

            if authfail_exception is not None:
                try:
                    af_exc = authfail_exception(action_id=action_id)
                except:
                    af_exc = authfail_exception()
                raise af_exc

            if authfail_result is AUTHFAIL_DONTCATCH:
                raise e

            return authfail_result

        try:
            return func(*p, **k)
        except dbus.DBusException, e:
            exc_name = e.get_dbus_name()

            if not exc_name.startswith(AUTH_EXC_PREFIX):
                raise

            if pkver == "0":
                # legacy PolicyKit versions need the frontend to acquire
                # authorizations
                action_id = exc_name[len(AUTH_EXC_PREFIX):]
                auth_interface = PolKit._polkit_auth_interface()
                obtained = auth_interface.ObtainAuthorization(action_id,
                        dbus.UInt32(0), dbus.UInt32(os.getpid()))
                if not obtained:
                    return handle_authfail(e)
            else:
                return handle_authfail(e)

    if func is not None:
        return decorator(_enable_proxy, func)
    else:
        def decorate(func):
            return decorator(_enable_proxy, func)
        return decorate

class NotAuthorizedException(dbus.DBusException):

    """Exception which a DBus service method throws if an authorization
    required for executing it can't be obtained."""

    _dbus_error_name = \
        "org.fedoraproject.slip.dbus.service.PolKit.NotAuthorizedException"

    def __init__(self, action_id, *p, **k):

        self._dbus_error_name = self.__class__._dbus_error_name + "."\
             + action_id
        super(NotAuthorizedException, self).__init__(*p, **k)


class VersionError(Exception):

    """Exception which gets thrown if no valid PolicyKit version can be
    determined."""


class PolKit(object):

    """Wrapper for PolicyKit which hides some of the differences between
    different PolicyKit versions."""

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
            timeout=method_call_no_timeout)

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
                                   timeout=method_call_no_timeout)


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


