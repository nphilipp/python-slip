#!/usr/bin/python
# -*- coding: utf-8 -*-

import gobject

import dbus
import dbus.service
import dbus.mainloop.glib

# FIND THE ACTUAL EXAMPLE CODE BELOW...

# try to find the module in the unpacked source tree

import sys
import os.path
import import_marker

# try to find the slip.dbus module

import imp

modfile = import_marker.__file__
path = os.path.dirname(modfile)
found = False
oldsyspath = sys.path
while not found and path and path != "/":
    path = os.path.abspath(os.path.join(path, os.path.pardir))
    try:
        slipmod = imp.find_module("slip", [path] + sys.path)
        if slipmod[1].startswith(path + "/"):
            found = True
            sys.path.insert(0, path)
            import slip.dbus.service
    except ImportError:
        pass

if not found:

    # fall back to system paths

    sys.path = oldsyspath
    import slip.dbus.service

# ...BELOW HERE:


class ExampleObject(slip.dbus.service.Object):

    def __init__(self, *p, **k):
        super(ExampleObject, self).__init__(*p, **k)
        self.config_data = """These are the contents of a configuration file.

They extend over some lines.

And one more."""
        print "service object constructed"

    def __del__(self):
        print "service object deleted"

    @slip.dbus.polkit.require_auth("org.fedoraproject.slip.example.read")
    @dbus.service.method("org.fedoraproject.slip.example.mechanism",
                         in_signature="", out_signature="s")
    def read(self):
        print "%s.read () -> '%s'" % (self, self.config_data)
        return self.config_data

    @slip.dbus.polkit.require_auth("org.fedoraproject.slip.example.write")
    @dbus.service.method("org.fedoraproject.slip.example.mechanism",
                         in_signature="s", out_signature="")
    def write(self, config_data):
        print "%s.write ('%s')" % (self, config_data)
        self.config_data = config_data


if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SessionBus()

    name = dbus.service.BusName("org.fedoraproject.slip.example.mechanism",
                                bus)
    object = ExampleObject(name, "/org/fedoraproject/slip/example/object")

    mainloop = gobject.MainLoop()
    slip.dbus.service.set_mainloop(mainloop)
    print "Running example service."
    mainloop.run()
