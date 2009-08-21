# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(0)")}
%{!?python_version: %global python_version %(%{__python} -c "from distutils.sysconfig import get_python_version; print get_python_version()")}

Name:       python-slip
Version:    0.1.15
Release:    1%{?dist}
Summary:    Miscellaneous convenience, extension and workaround code for Python

Group:      System Environment/Libraries
License:    GPLv2+
URL:        http://fedorahosted.org/python-slip
Source0:    http://fedorahosted.org/releases/$(echo %{name} | %{__sed} 's@\(\(.\)\(.\).*\)@\2/\3/\1@')/%{name}-%{version}.tar.bz2
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:  noarch

BuildRequires:  python
BuildRequires:  python-devel

%description
The Simple Library for Python packages contain miscellaneous code for
convenience, extension and workaround purposes.

This package provides the "slip" base module.

%package dbus
Summary:    Convenience functions for dbus services
Group:      System Environment/Libraries
Requires:   %{name} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:   dbus-python >= 0.80
%if 0%{?fedora}%{?rhel} && 0%{?fedora} < 12 && 0%{?rhel} < 6
Requires:   PolicyKit >= 0.8-3
%else
Conflicts:  PolicyKit < 0.8-3
Requires:   polkit >= 0.94
%endif

%description dbus
The Simple Library for Python packages contain miscellaneous code for
convenience, extension and workaround purposes.

This package provides slip.dbus.service.Object, which is a dbus.service.Object
derivative that ends itself after a certain time without being used and/or if
there are no clients anymore on the message bus, as well as convenience
functions and decorators for integrating a dbus service with PolicyKit.

%package gtk
Summary:    Code to make auto-wrapping gtk labels
Group:      System Environment/Libraries
Requires:   %{name} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:   pygtk2

%description gtk
The Simple Library for Python packages contain miscellaneous code for
convenience, extension and workaround purposes.

This package provides slip.gtk.set_autowrap(), a convenience function which
lets gtk labels be automatically re-wrapped upon resizing.

%prep
%setup -q

%build
make %{?_smp_mflags}

%install
rm -rf %buildroot
make install DESTDIR=%buildroot

%clean
rm -rf %buildroot

%files
%defattr(-,root,root,-)
%doc COPYING
%dir %{python_sitelib}/slip/
%{python_sitelib}/slip/__init__.py*
%{python_sitelib}/slip/util
%{python_sitelib}/slip-%{version}-py%{python_version}.egg-info

%files dbus
%defattr(-,root,root,-)
%doc doc/dbus/*
%{python_sitelib}/slip/dbus
%{python_sitelib}/slip.dbus-%{version}-py%{python_version}.egg-info

%files gtk
%defattr(-,root,root,-)
%{python_sitelib}/slip/gtk
%{python_sitelib}/slip.gtk-%{version}-py%{python_version}.egg-info

%changelog
* Fri Aug 21 2009 Nils Philippsen <nils@redhat.com>
- require polkit >= 0.94 from F-12 on

* Thu Nov 27 2008 Nils Philippsen <nphilipp@redhat.com
- use fedorahosted.org URLs

* Tue Oct 14 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.15
- add slip.dbus.polkit.AreAuthorizationsObtainable()

* Mon Sep 15 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.14
- clarify examples a bit

* Tue Sep 09 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.13
- add working examples

* Fri Aug 29 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.12
- make slip.dbus.service.Object persistence overridable per object

* Tue Aug 05 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.11
- implement freezing/thawing hooks

* Tue Aug 05 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.10
- implement disabling/enabling hooks

* Tue Aug 05 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.9
- make slip.util.hookable more flexible, easier extendable

* Mon Aug 04 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.8
- add slip.util.hookable

* Thu Jul 24 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.7
- fix import error (#456511)

* Wed Jul 23 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.6
- move proxy.polkit_enable to polkit.enable_proxy
- rename polkit.NotAuthorized to NotAuthorizedException, polkit.auth_required
  to require_auth

* Tue Jul 22 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.5
- don't reset timeout on failed polkit authorizations

* Mon Jul 21 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.4
- implement PolicyKit convenience functions and decorators
- rename slip.dbus.service.TimeoutObject -> slip.dbus.service.Object

* Fri Jul 11 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.3
- BR: python-devel

* Fri Jul 11 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.2
- fix more inconsistent tabs/spaces

* Fri Jul 11 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1.1
- fix inconsistent tabs/spaces

* Tue May 27 2008 Nils Philippsen <nphilipp@redhat.com> - 0.1
- move gtk.py -> gtk/__init__.py
- rename gtk.set_autowrap () -> gtk.label_autowrap ()

* Mon May 26 2008 Nils Philippsen <nphilipp@redhat.com>
- initial build
