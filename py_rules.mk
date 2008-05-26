ifndef DESTDIR
	DESTDIR = /
endif

ifndef PY_SOURCES
	PY_SOURCES = $(wildcard src/*.py)
endif

setup.py:	setup.py.in $(PKGNAME).spec
	sed -e 's/@VERSION@/$(PKGVERSION)/g' < $< > $@

py-build-ext:	setup.py $(PY_SOURCES)
	python setup.py build_ext -i

py-build:   setup.py $(PY_SOURCES)
	python setup.py build

py-install:
	python setup.py install -O1 --skip-build --root $(DESTDIR)

py-clean:
	python setup.py clean
	rm -f setup.py

py-check:
	pychecker -F pycheckrc $(PY_SOURCES)

