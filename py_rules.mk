# License: GPL v2 or later
# Copyright Red Hat Inc. 2008

ifndef DESTDIR
	DESTDIR = /
endif

ifndef PY_SOURCES
	PY_SOURCES = $(wildcard src/*.py)
endif

ifndef SETUP_PY
	SETUP_PY = setup.py
endif

_SETUP_PY = $(PY_SRC_DIR)/$(SETUP_PY)

$(_SETUP_PY):	$(_SETUP_PY).in $(PKGNAME).spec
	cd $(PY_SRC_DIR); \
	sed -e 's/@VERSION@/$(PKGVERSION)/g' < $< > $@

py-build-ext:	$(_SETUP_PY) $(PY_SOURCES)
	cd $(PY_SRC_DIR); \
	python $(SETUP_PY) build_ext -i

py-build:   $(_SETUP_PY) $(PY_SOURCES)
	cd $(PY_SRC_DIR); \
	python $(SETUP_PY) build

py-install:	$(_SETUP_PY)
	cd $(PY_SRC_DIR); \
	python $(SETUP_PY) install -O1 --skip-build --root $(DESTDIR)

py-clean:	$(_SETUP_PY)
	cd $(PY_SRC_DIR); \
	python $(SETUP_PY) clean; \
	rm -f $(SETUP_PY)

py-check:
	pychecker -F pycheckrc $(PY_SOURCES)

