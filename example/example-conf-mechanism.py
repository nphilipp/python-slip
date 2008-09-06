#!/usr/bin/python

import gobject

import dbus
import dbus.service
import dbus.mainloop.glib

try:
    import slip.dbus.service
except ImportError:
    import sys
    import os.path
    import example_service

    # try to find the slip.dbus module

    modfile = example_service.__file__
    path = os.path.dirname (modfile)
    found = False
    oldsyspath = sys.path
    while not found and path and path != "/":
        path = os.path.abspath (os.path.join (path, os.path.pardir))
        sys.path = oldsyspath + [path]
        try:
            import slip.dbus.service
            found = True
        except ImportError:
            pass
    if not found:
        import slip.dbus.service
    sys.path = oldsyspath

class ExampleObject(slip.dbus.service.Object):
    def __init__ (self, *p, **k):
        super (ExampleObject, self).__init__ (*p, **k)
        self.config_data = """These are the contents of a configuration file.

They extend over some lines.

And one more."""
        print "service object constructed"

    def __del__ (self):
        print "service object deleted"

    @slip.dbus.polkit.require_auth ("org.fedoraproject.slip.example.read")
    @dbus.service.method ("org.fedoraproject.slip.example.mechanism",
                          in_signature='', out_signature='s')
    def read (self):
        print "%s.read () -> '%s'" % (self, self.config_data)
        return self.config_data

    @slip.dbus.polkit.require_auth ("org.fedoraproject.slip.example.write")
    @dbus.service.method("org.fedoraproject.slip.example.mechanism",
                         in_signature='s', out_signature='')
    def write (self, config_data):
        print "%s.write ('%s')" % (self, config_data)
        self.config_data = config_data

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus ()

    name = dbus.service.BusName ("org.fedoraproject.slip.example.mechanism", bus)
    object = ExampleObject (bus, '/org/fedoraproject/slip/example/object')

    mainloop = gobject.MainLoop ()
    slip.dbus.service.set_mainloop (mainloop)
    print "Running example service."
    mainloop.run ()
