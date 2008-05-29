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

$(SETUP_PY):	$(SETUP_PY).in $(PKGNAME).spec
	sed -e 's/@VERSION@/$(PKGVERSION)/g' < $< > $@

py-build-ext:	$(SETUP_PY) $(PY_SOURCES)
	python $(SETUP_PY) build_ext -i

py-build:   $(SETUP_PY) $(PY_SOURCES)
	python $(SETUP_PY) build

py-install:
	python $(SETUP_PY) install -O1 --skip-build --root $(DESTDIR)

py-clean:
	python $(SETUP_PY) clean
	rm -f $(SETUP_PY)

py-check:
	pychecker -F pycheckrc $(PY_SOURCES)

