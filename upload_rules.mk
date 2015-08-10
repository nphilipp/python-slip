# License: GPL v2 or later
# Copyright Red Hat Inc. 2008, 2015

ifndef UPLOAD_METHOD
UPLOAD_METHOD = scp
endif

PKGARCHIVE=$(PKGNAME)-$(PKGVERSION).tar.bz2

ifeq ($(UPLOAD_METHOD),scp)
ifdef UNSTABLE

upload:
	@echo Use of target \'$@\' not possible in unstable branch. >&2
	@exit 1

else ifdef UPLOAD_URL

upload:
	@url="$(UPLOAD_URL)"; \
	case "$$url" in \
	ssh://*) \
		url="$${url#ssh://}"; \
		userhostname="$${url%%/*}"; \
		path="$${url#*/}"; \
		echo Copying "$(PKGNAME)-$(PKGVERSION).tar.bz2" to "$$userhostname:$$path"; \
		scp "$(PKGNAME)-$(PKGVERSION).tar.bz2" "$$userhostname:$$path"; \
		;; \
	*) \
		echo Unknown method. >&2; \
		exit 1; \
		;; \
	esac

else

upload:
	@echo "UPLOAD_URL undefined!" >&2
	@false

endif
else ifeq ($(UPLOAD_METHOD),github)

include github_rules.mk
upload:	github-upload

endif
