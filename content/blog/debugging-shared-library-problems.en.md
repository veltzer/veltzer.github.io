+++
title = "Debugging shared library problems"
date = 2011-05-13

[taxonomies]
tags = ["linux", "debugging"]
+++

A tip: sometimes you install stuff from source and library search order makes analyzing which library you are actually using a mess. A useful tool is `ldconfig -p` that will print the cache of the dynamic linker for you allowing you to understand which libraries are actually being used.
