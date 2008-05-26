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

class DemoException(dbus.DBusException):
    _dbus_error_name = 'org.fedoraproject.slip.Example.DemoException'

class SomeObject(slip.dbus.service.TimeoutObject):
    def __init__ (self, *p, **k):
        super (SomeObject, self).__init__ (*p, **k)
        print "service object constructed"

    def __del__ (self):
        print "service object deleted"

    @dbus.service.method("org.fedoraproject.slip.Example.SampleInterface",
                         in_signature='s', out_signature='as')
    def HelloWorld(self, hello_message):
        return ["Hello", " from example-service.py", "with unique name",
                system_bus.get_unique_name()]

    @dbus.service.method("org.fedoraproject.slip.Example.SampleInterface",
                         in_signature='', out_signature='')
    def RaiseException(self):
        raise DemoException('The RaiseException method does what you might '
                            'expect')

    @dbus.service.method("org.fedoraproject.slip.Example.SampleInterface",
                         in_signature='', out_signature='(ss)')
    def GetTuple(self):
        return ("Hello Tuple", " from example-service.py")

    @dbus.service.method("org.fedoraproject.slip.Example.SampleInterface",
                         in_signature='', out_signature='a{ss}')
    def GetDict(self):
        return {"first": "Hello Dict", "second": " from example-service.py"}

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # with a real service, this may also be a dbus.SystemBus instead
    system_bus = dbus.SessionBus ()

    name = dbus.service.BusName("org.fedoraproject.slip.Example", system_bus)
    object = SomeObject(system_bus, '/org/fedoraproject/slip/Example/SomeObject')

    mainloop = gobject.MainLoop()
    slip.dbus.service.set_mainloop (mainloop)
    print "Running example service."
    mainloop.run ()
