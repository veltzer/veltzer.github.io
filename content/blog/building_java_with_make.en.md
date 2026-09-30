+++
title = "Building Java With a Makefile Instead of Ant"
date = 2011-03-06

[taxonomies]
tags = ["programming", "java"]
+++

Every Java project I meet comes with a `build.xml`, and every `build.xml` is several hundred lines of XML that does what a fifteen-line Makefile does for every other language on the machine. I build my Java with `make`. Here is how, and here is the honest account of what you gain and what you give up.

## The Makefile

The layout is the conventional one: sources under `src/`, compiled classes under `build/`, and one jar as the product.

```makefile
JAVAC := javac
JAR := jar
JAVAC_FLAGS := -Xlint:all -encoding UTF-8

SRC_DIR := src
BUILD_DIR := build
JAR_FILE := myapp.jar
MAIN_CLASS := com.example.Main

SOURCES := $(shell find $(SRC_DIR) -name '*.java')
CLASSES := $(patsubst $(SRC_DIR)/%.java,$(BUILD_DIR)/%.class,$(SOURCES))

.PHONY: all clean run

all: $(JAR_FILE)

$(BUILD_DIR)/%.class: $(SRC_DIR)/%.java
	@mkdir -p $(BUILD_DIR)
	$(JAVAC) $(JAVAC_FLAGS) -d $(BUILD_DIR) -cp $(BUILD_DIR):$(SRC_DIR) $<

$(JAR_FILE): $(CLASSES)
	$(JAR) cfe $@ $(MAIN_CLASS) -C $(BUILD_DIR) .

run: $(JAR_FILE)
	java -jar $(JAR_FILE)

clean:
	rm -rf $(BUILD_DIR) $(JAR_FILE)
```

The pattern rule maps each source to its class file, so `make` compiles only the sources that changed. The `-cp` argument includes both the build directory (for classes already compiled) and the source directory (so `javac` can find the sources of classes that have not been compiled yet). The jar rule uses `-e` to set the entry point in the manifest, so the result runs with `java -jar`.

If you have third-party jars, put them in `lib/` and add them to the classpath:

```makefile
LIBS := $(wildcard lib/*.jar)
CLASSPATH := $(BUILD_DIR):$(SRC_DIR):$(subst $(eval) ,:,$(LIBS))
```

and use `-cp $(CLASSPATH)` in the compile rule.

## What You Gain

**One tool for everything.** A project is rarely only Java. There is a C library with a JNI wrapper, a Python script that generates a source file, a LaTeX manual, a shell script that packages the release. Ant knows about Java. `make` knows about files and commands, which is what all of those are. The same `make all` builds the whole tree, and the dependencies between the Java and the non-Java parts are expressed in the same language as the dependencies inside each.

**Real dependencies.** A Makefile is a dependency graph and nothing else. Ant's targets are a list of steps to run; its notion of what is up to date is whatever each task happens to implement, and the `javac` task's answer is to compare source and class timestamps for the files it is handed. `make` does the same comparison, but it does it for every rule, including the rules you wrote for the generated sources and the packaging, uniformly, and it lets you say that the jar depends on the manifest template and the manifest template depends on the version file.

**No XML.** This is not an aesthetic complaint. A build description is code, and XML is a poor language for code: verbose, hard to diff, and with no way to compute anything without dropping into a plugin. A Makefile has variables, functions, pattern rules, and shell.

**It is already there.** Every Unix machine has `make`. Nobody has to install a build tool to build the project.

## What You Give Up

**Incremental compilation is not what it looks like.** The pattern rule recompiles a changed source, but Java classes depend on other classes in ways that the filesystem does not show. Change a constant in `A.java` and `B.class`, which inlined that constant, is now wrong, and `make` has no idea because `B.java` did not change. Ant has exactly the same problem and hides it just as badly. The honest fix in both cases is `make clean` before a release build, and `javac` on the whole source set for any change that touches interfaces. For a project of ordinary size the full compile takes seconds, so the incremental rule is a convenience during development and not something to trust.

**Classpath handling is manual.** Ant's `<path>` and `<fileset>` elements, and later Ivy and Maven, manage jar collections for you. With `make` you list them, as above, and you resolve their dependencies yourself. For a project with three jars in `lib/` this is trivial. For one with forty transitive dependencies it is a real cost, and it is the strongest argument for the Java-specific tools.

**Java people do not expect it.** A contributor who opens the project and does not find `build.xml` or `pom.xml` will be confused for a minute. That is a minute, and the Makefile is short enough to read in it, but it is a real friction and I do not pretend otherwise.

## Where I Come Down

For a project that is mostly Java and has a large dependency tree, use the tool the dependency tree wants. For everything else, and especially for anything that mixes Java with other languages, the Makefile is simpler, more honest about what depends on what, and does not add a build system to the list of things a new contributor must learn. The fifteen lines above have built every Java program I have written for years, and I have never once missed the XML.
