# License: GPL v2 or later
# Copyright Red Hat Inc. 2008, 2015

PKGNAME=python-slip
UNSTABLE=1

SCM_REMOTEREPO_RE = ^ssh://(.*@)?github.com:nphilipp/$(PKGNAME).git$
UPLOAD_METHOD = github
GITHUB_PROJECT = https://github.com/nphilipp/$(PKGNAME)

PY_SOURCES = $(wildcard slip/*.py slip/dbus/*.py slip/gtk/*.py)

all:	py-build
	
include rpmspec_rules.mk
include py_rules.mk
include git_rules.mk
include upload_rules.mk

install:	py-install

clean:	py-clean
