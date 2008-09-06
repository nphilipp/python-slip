
servicedir = /usr/share/dbus-1/system-services
service_DATA = org.fedoraproject.slip.example.mechanism.service

confdir = /etc/dbus-1/system.d
conf_DATA = org.fedoraproject.slip.example.mechanism.conf

policydir = /usr/share/PolicyKit/policy
policy_DATA = org.fedoraproject.slip.example.policy

libexecdir = /usr/local/libexec
libexec_SCRIPTS = example-conf-mechanism.py

example_install:
	install -d $(libexecdir)
	install -m0755 $(libexec_SCRIPTS) $(libexecdir)
	install -d $(servicedir)
	install -m0644 $(service_DATA) $(servicedir)
	install -d $(confdir)
	install -m0644 $(conf_DATA) $(confdir)
	install -d $(policydir)
	install -m0644 $(policy_DATA) $(policydir)
	-/sbin/restorecon -v -R $(libexecdir) $(servicedir) $(confdir) $(policydir)

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
	for p in $(policy_DATA); do \
		rm -f "$(policydir)/$$p"; \
	done
