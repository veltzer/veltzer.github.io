##############
# parameters #
##############
# do you want to show the commands executed ?
DO_MKDBG:=0
# do you want dependency on the Makefile itself ?
DO_ALLDEP:=1
# do you want to check the javascript code?
DO_JS_CHECK:=1
# do you want to do js packaging?
DO_JS_PACKAGE:=0

########
# code #
########
HTML_SRC:=$(shell find docs -type f -and -name "*.html")
HTML_CHECK:=$(addprefix out/, $(addsuffix .check, $(basename $(HTML_SRC))))

PKG_SRC:=$(shell find pkg -type f -and -name "*.txt")
PKG_CHECK:=$(addprefix out/, $(addsuffix .check, $(basename $(PKG_SRC))))

# silent stuff
ifeq ($(DO_MKDBG),1)
Q:=
# we are not silent in this branch
else # DO_MKDBG
Q:=@
#.SILENT:
endif # DO_MKDBG

ifeq ($(DO_JS_CHECK),1)
ALL+=$(HTML_CHECK)
endif # DO_JS_CHECK

ifeq ($(DO_JS_PACKAGE),1)
ALL+=$(PKG_CHECK)
endif # DO_JS_PACKAGE

#########
# rules #
#########
.PHONY: all
all: $(ALL)
	@true

.PHONY: debug
debug:
	$(info ALL is $(ALL))
	$(info JSON is $(JSON))
	$(info JSON_CHECK is $(JSON_CHECK))
	$(info YAML is $(YAML))
	$(info YAML_JSON is $(YAML_JSON))
	$(info HTML_SRC is $(HTML_SRC))
	$(info HTML_CHECK is $(HTML_CHECK))
	$(info PKG_SRC is $(PKG_SRC))
	$(info PKG_CHECK is $(PKG_CHECK))

.PHONY: clean
clean:
	$(Q)rm -rf out
.PHONY: clean_hard
clean_hard:
	$(info doing [$@])
	$(Q)git clean -qffxd

############
# patterns #
############
$(JSON_CHECK): out/check/%.stamp: %
	$(info doing [$@])
	$(Q)pymakehelper only_print_on_error python -m json.tool $<
	$(Q)pymakehelper only_print_on_error check-jsonschema --schemafile $$(yq -r '.["$$schema"]' $<)  $<
	$(Q)pymakehelper touch_mkdir $@
# $(Q)pymakehelper only_print_on_error check-jsonschema --check-metaschema $<
# $(Q)node_modules/.bin/ajv compile -r "docs/json/shared/common.json" -c ajv-formats -s $<
$(YAML_CHECK): out/check/%.stamp: %
	$(info doing [$@])
	$(Q)pycmdtools validate_yaml $<
	$(Q)pymakehelper touch_mkdir $@
$(HTML_CHECK): out/%.check: %.html .jshintrc
	$(info doing [$@])
	$(Q)node_modules/.bin/jshint --extract=auto $<
	$(Q)pymakehelper touch_mkdir $@
$(PKG_CHECK): out/%.check: %.txt scripts/package.sh
	$(info doing [$@])
	$(Q)scripts/package.sh -j docs/$(basename $(notdir $<)).js -c docs/$(basename $(notdir $<)).css $<
	$(Q)pymakehelper touch_mkdir $@

# $(JSON_VALIDATE): out/validate/%.stamp: %
# 	$(info doing [$@])
# 	$(Q)jsonschema -i $< schemas/json/$(basename $(notdir $@))
#	$(Q)pymakehelper touch_mkdir $@
# $(YAMLS_JSON): out/yaml2json/%.yaml: %
# 	$(info doing [$@])
# 	$(Q)mkdir -p $(dir $@)
# 	$(Q)yq . < $< > $@

##########
# alldep #
##########
ifeq ($(DO_ALLDEP),1)
.EXTRA_PREREQS+=$(foreach mk, ${MAKEFILE_LIST},$(abspath ${mk}))
endif # DO_ALLDEP
