+++
title = "Tests Are Build Products, and the Build System Should Own Them"
date = 2012-03-11

[taxonomies]
tags = ["programming", "opinion"]
+++

Most projects treat tests as a separate ceremony. There is the build, which produces the binaries, and then there is "running the tests", which is a different command, run at a different time, usually by a different mechanism: a test runner, a CI script, a Makefile target called `test` that depends on nothing and rebuilds nothing. The two are joined by convention and by habit, not by anything the tools understand.

I think this is backwards, and the reason is not aesthetic. **A test is a build product like any other: it has inputs, it has an output, and the output is stale exactly when the inputs change.** Once you say it that way, the build system is the obvious owner, and the separate test runner is a reimplementation of dependency tracking done badly.

## What a Test Actually Is

Strip a test down to what it does. It takes a set of inputs, the code under test, the test code itself, any fixtures or data files, and produces an output: pass or fail, plus a log. That is precisely the shape of a compilation step. The compiler takes sources and headers and produces an object file; the test takes sources and fixtures and produces a verdict.

The build system already knows how to handle this shape. It knows what depends on what. It knows that if you touched `parser.c` then `parser.o` must be rebuilt, and everything that links `parser.o` after it. What it is usually not told is that `test_parser.passed` must also be rebuilt, and that nothing else depends on `parser.c` in any interesting way.

Tell it. Make the test's result a file:

```makefile
test_parser.passed: test_parser parser.o fixtures/parser_cases.txt
	./test_parser && touch $@

check: test_parser.passed test_lexer.passed test_io.passed
```

Now the build system does the rest for free. Touch a fixture and only the tests that read it rerun. Touch a header used everywhere and every test reruns, as it should. Touch nothing and `make check` finishes in the time it takes to stat a few files.

## Why the Separate Runner Is the Wrong Tool

The usual alternative is a test runner that discovers every test and runs all of them, every time. It has two failure modes, and they pull in opposite directions.

**It runs too much.** On a large project the full suite takes minutes or hours, so people stop running it locally. They push and wait for the CI machine to tell them, twenty minutes later, that they broke something they could have caught in two seconds. The suite that is too slow to run is a suite that does not get run, and a test that does not get run is documentation.

**Then it runs too little.** To fight the first problem people start selecting: run only the tests in this directory, only the tests tagged `fast`, only the tests I think are relevant. Now the selection is done by a human guessing at dependencies, which is exactly the job the build system exists to do mechanically. The guess is wrong often enough that the twenty-minute CI failure comes back.

A test runner cannot solve this because it does not know the dependency graph. It knows which files are tests. It does not know which tests care about the file you just changed. The build system knows, because that knowledge is the entire content of a build system.

## The Objections

**Tests have side effects.** Some do: they write to a database, they bind a port, they need a service running. Those are integration tests, and they should be modelled as what they are, a product that depends on the environment. Encode the environment as an input if you can, and if you cannot, at least make the build fail loudly rather than pretend. Most tests do not have this problem, and the ones that do are not an argument for treating the other ninety percent badly.

**Flaky tests will be cached as passed.** A test that passes once and fails later with no input change is not a test, it is a random number generator, and caching its output exposes that rather than causing it. The remedy is to fix the flake, and the build system helps here too: when a cached pass turns into a failure with nothing upstream changed, you have found a flake with certainty instead of a suspicion.

**The build gets slower.** Only the first time. After that it gets faster than any runner, because it does the minimum.

## The Deeper Point

The reason this matters beyond convenience is that it changes what the word "built" means. A tree where the build succeeded but the tests were not run is in an unknown state, and we have all learned to treat it as good anyway because the tests were somebody else's problem. Fold the tests into the build and **a successful build means the tests that could have been affected by your change have passed**. Nothing more, nothing less, and mechanically true rather than hopefully true.

That is the most sane way to connect tests to their dependencies, because it is the only way that connects them at all. Everything else is a person remembering to do it.
