#!/usr/bin/python

import dbus
import time

session_bus = dbus.SessionBus ()

someobj = session_bus.get_object ("org.fedoraproject.slip.Example", "/org/fedoraproject/slip/Example/SomeObject")

for i in xrange (3):
    print someobj.HelloWorld ("foo", dbus_interface = "org.fedoraproject.slip.Example.SampleInterface")
    time.sleep (2)
