# License: GPL v2 or later
# Copyright Red Hat Inc. 2015

ifdef GITHUB_PROJECT

VARS_OLD := $(filter-out GITHUB_PROJECT,$(.VARIABLES))

ifndef UNSTABLE
_GH_PRERELEASE = false
else
_GH_PRERELEASE = true
endif

_GH_FILE = $(lastword $(MAKEFILE_LIST))
_GH_DIR = $(shell dirname "$(_GH_FILE)")

_GH_TOKEN_FILE = $(_GH_DIR)/.github-token
_GH_TOKEN = $(shell cat "$(_GH_TOKEN_FILE)")
_GH_CURL = curl -s --header 'Authorization: token $(_GH_TOKEN)'

_GH_PROJ = $(shell x="$(GITHUB_PROJECT)"; echo $${x\#*://github.com/})
_GH_OWNER = $(shell x="$(_GH_PROJ)"; echo $${x%/*})
_GH_REPO = $(shell x="$(_GH_PROJ)"; echo $${x\#*/})

_GH_API = https://api.github.com/repos
_GH_API_REPO = $(_GH_API)/$(_GH_OWNER)/$(_GH_REPO)
_GH_API_REL = $(_GH_API_REPO)/releases

_GH_TAG_COMMITISH = $(shell git rev-parse $(SCM_TAG))

_gh_tagged_rel = $(_GH_CURL) '$(_GH_API_REL)/tags/$(SCM_TAG)'

_gh_tag_rel = $(_GH_CURL) '$(_GH_API_REL)' \
			  -d '{"prerelease":$(_GH_PRERELEASE),"tag_name":"$(SCM_TAG)","target_commitish":"$(_GH_TAG_COMMITISH)","name":"$(SCM_TAG)"}'

VARS_OLD := $(.VARIABLES)

$(foreach v,                                        \
	$(filter-out $(VARS_OLD) VARS_OLD,$(.VARIABLES)), \
	$(info $(v) = $($(v))))

github-upload:
	@if [ ! -e "$(_GH_TOKEN_FILE)" ]; then \
		echo "Github authentication token file '$(_GH_TOKEN_FILE)' missing" >&2; \
		exit 1; \
	fi
	@if ! type -path file >/dev/null; then \
		echo "'file' binary not found" >&2; \
		exit 1; \
	fi
	@if ! type -path jq >/dev/null; then \
		echo "'jq' binary not found" >&2; \
		exit 1; \
	fi
	@gh_tagged_rel_out="$$($(_gh_tagged_rel))"; \
	echo "Checking tagged release $(SCM_TAG)"; \
	rel_id="$$(echo "$$gh_tagged_rel_out" | jq .id)"; \
	if [ "$$rel_id" = "null" ]; then \
		echo "Creating tagged release $(SCM_TAG)"; \
		gh_tagged_rel_out="$$($(_gh_tag_rel))"; \
		rel_id="$$(echo "$$gh_tagged_rel_out" | jq .id)"; \
	fi; \
	if [ "$$rel_id" -eq "$$rel_id" ]; then \
		mimetype="$$(file --brief --mime-type $(PKGARCHIVE))"; \
		upload_url="$$(echo "$$gh_tagged_rel_out" | jq .upload_url)"; \
		upload_url="$${upload_url#\"}"; \
		upload_url="$${upload_url%\"}"; \
		echo -n "Uploading $(PKGARCHIVE)... "; \
		upload_out="$$($(_GH_CURL) \
			--header "Content-Type: $$mimetype" \
			--header "Accept: application/vnd.github.manifold-preview" \
			--data-binary "@$(PKGARCHIVE)" \
			"$${upload_url%\{\?name\}}?name=$(PKGARCHIVE)")"; \
		if [ "$$(echo "$$upload_out" | jq .state)" = "\"uploaded\"" ]; then \
			echo done; \
		else \
			echo failed; \
			echo "$$upload_out" | jq . >&2; \
		fi; \
	fi

else

github-upload:
	@echo "GITHUB_PROJECT undefined!" >&2
	@false

endif
