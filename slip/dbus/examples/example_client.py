#!/usr/bin/python

import dbus
import time

system_bus = dbus.SystemBus ()

someobj = system_bus.get_object ("org.fedoraproject.slip.Example", "/org/fedoraproject/slip/Example/SomeObject")

for i in xrange (3):
    print someobj.HelloWorld ("foo", dbus_interface = "org.fedoraproject.slip.Example.SampleInterface")
    time.sleep (2)
