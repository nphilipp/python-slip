#!/usr/bin/python

import dbus

system_bus = dbus.SystemBus ()

from slip.dbus import polkit

class DBusProxy (object):
    def __init__ (self):
        self.bus = dbus.SystemBus ()
        self.dbus_object = bus.get_object ("org.fedoraproject.config.example.mechanism", "/org/fedoraproject/config/example/object")

    @polkit.enable_proxy
    def read (self):
        return self.dbus_object.read (dbus_interface = "org.fedoraproject.config.example.mechanism")

    @polkit.enable_proxy
    def write (self, config_data):
        return self.dbus_object.write (config_data, dbus_interface = "org.fedoraproject.config.example.mechanism")

example_object = DBusProxy ()

config_data = example_object.read ()

print "read config_data successfully:"
print config_data
print
print

print "attempting to write config data"

example_object.write (config_data)

print "successfully wrote config data"
