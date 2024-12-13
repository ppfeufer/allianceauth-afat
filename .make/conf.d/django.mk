# Make targets for Django projects

# Translation files
.PHONY: translations
translations:
	@echo "Creating or updating translation files"
	@django-admin makemessages \
		-l cs_CZ \
		-l de \
		-l es \
		-l fr_FR \
		-l it_IT \
		-l ja \
		-l ko_KR \
		-l nl_NL \
		-l pl_PL \
		-l ru \
		-l sk \
		-l uk \
		-l zh_Hans \
		--keep-pot \
		--ignore 'build/*'
	@current_app_version=$$(pip show $(appname) | grep 'Version: ' | awk '{print $$NF}'); \
	echo "Current app version: $$current_app_version"; \
	sed -i "/\"Project-Id-Version: /c\\\"Project-Id-Version: $(appname_verbose) $$current_app_version\\\n\"" $(translation_template); \
	sed -i "/\"Report-Msgid-Bugs-To: /c\\\"Report-Msgid-Bugs-To: $(git_repository_issues)\\\n\"" $(translation_template);

# Compile translation files
.PHONY: compile_translations
compile_translations:
	@echo "Compiling translation files"
	@django-admin compilemessages \
		-l cs_CZ \
		-l de \
		-l es \
		-l fr_FR \
		-l it_IT \
		-l ja \
		-l ko_KR \
		-l nl_NL \
		-l pl_PL \
		-l ru \
		-l sk \
		-l uk \
		-l zh_Hans

# Help message
.PHONY: help
help::
	@echo "  $(TEXT_UNDERLINE)Translation:$(TEXT_UNDERLINE_END)"
	@echo "    translations              Create or update translation files"
	@echo "    compile_translations      Compile translation files"
	@echo ""
