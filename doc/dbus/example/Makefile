
servicedir = /usr/share/dbus-1/system-services
service_DATA = org.fedoraproject.slip.example.mechanism.service

confdir = /etc/dbus-1/system.d
conf_DATA = org.fedoraproject.slip.example.mechanism.conf

policy0dir = /usr/share/PolicyKit/policy
policy0_DATA = org.fedoraproject.slip.example.policy

policy1dir = /usr/share/polkit-1/actions
policy1_DATA = org.fedoraproject.slip.example.policy

libexecdir = /usr/local/libexec
libexec_SCRIPTS = example-conf-mechanism.py

all:
	@echo Use "make <target>". Targets are:
	@echo example_install
	@echo example_uninstall

example_install:
	install -d $(libexecdir)
	install -m0755 $(libexec_SCRIPTS) $(libexecdir)
	install -d $(servicedir)
	install -m0644 $(service_DATA) $(servicedir)
	install -d $(confdir)
	install -m0644 $(conf_DATA) $(confdir)
	install -d $(policy0dir)
	install -m0644 $(policy0_DATA) $(policy0dir)
	install -d $(policy1dir)
	install -m0644 $(policy1_DATA) $(policy1dir)
	-/sbin/restorecon -v -R $(libexecdir) $(servicedir) $(confdir) $(policy0dir) $(policy1dir)

example_uninstall:
	for p in $(libexec_SCRIPTS); do \
		rm -f "$(libexecdir)/$$p"; \
	done
	for p in $(service_DATA); do \
		rm -f "$(servicedir)/$$p"; \
	done
	for p in $(conf_DATA); do \
		rm -f "$(confdir)/$$p"; \
	done
	for p in $(policy0_DATA); do \
		rm -f "$(policy0dir)/$$p"; \
	done
	for p in $(policy1_DATA); do \
		rm -f "$(policy1dir)/$$p"; \
	done
