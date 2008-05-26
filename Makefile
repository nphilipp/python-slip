# License: GPL v2 or later
# Copyright Red Hat Inc. 2008

PKGNAME=python-slip
PKGVERSION=$(shell awk '/Version:/ { print $$2 }' $(PKGNAME).spec)

SCM_REMOTEREPO_RE = ^ssh://fedorapeople.org/~nphilipp/public_html/git/$(PKGNAME).git$
UPLOAD_URL = ssh://fedorapeople.org/~nphilipp/public_html/$(PKGNAME)/

PY_SOURCES = $(wildcard slip/*.py slip/dbus/*.py slip/gtk/*.py)

all:	py-build
	
include py_rules.mk
include git_rules.mk
include upload_rules.mk

install:	py-install

clean:	py-clean
