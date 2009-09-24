# -*- coding: utf-8 -*-

# slip.dbus.proxies -- slightly augmented dbus proxy classes
#
# Copyright © 2005-2007 Collabora Ltd. <http://www.collabora.co.uk/>
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

"""This module contains D-Bus proxy classes which implement the default
timeout of the augmented bus classes in slip.dbus.bus."""

import dbus
import dbus.proxies


class _ProxyMethod(dbus.proxies._ProxyMethod):

    def __call__(self, *args, **kwargs):
        default_timeout = getattr(self._proxy._bus, "default_timeout", -1.0)
        kwargs.setdefault("timeout", default_timeout)

        # older dbus versions don't know "no timeout", so make it as large as
        # it gets

        if dbus.version < (0, 84, 0) and kwargs["timeout"] is None:
            from gobject import G_MAXINT

            # timeout is x seconds in dbus-python, but milliseconds in the dbus
            # library

            kwargs["timeout"] = G_MAXINT / 1000

        return dbus.proxies._ProxyMethod.__call__(self, *args, **kwargs)


class ProxyObject(dbus.proxies.ProxyObject):

    ProxyMethodClass = _ProxyMethod


