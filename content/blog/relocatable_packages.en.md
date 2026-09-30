+++
title = "Software Should Not Care Where It Was Installed"
date = 2012-04-15

[taxonomies]
tags = ["linux", "programming", "opinion"]
+++

Take a program that was built to live in `/usr` and copy it to `/opt/myapp`. On Unix, more often than not, it breaks. It cannot find its shared libraries, or its configuration, or its data files, or its plugins, because every one of those paths was baked into the binary at compile time as an absolute string. This is so normal on Unix that we stopped noticing it is a defect. It is a defect, and it has always been fixable.

## What Gets Baked In

A typical build hardcodes three kinds of location. The library search path: where the dynamic linker looks for the `.so` files the program needs. The data prefix: where the program looks for its icons, translations, templates and help files. The configuration path: where it reads its settings. Configure with `--prefix=/usr` and all three become literal strings inside the executable.

Move the executable and every one of those strings is now wrong. The program was not installed; it was welded.

## The Library Path: `$ORIGIN`

The dynamic linker has supported relocation for a long time, and most people have never used it. When a binary is linked with an rpath, the linker searches that path for libraries. The rpath may contain the token `$ORIGIN`, which the linker replaces at run time with the directory the executable itself lives in:

```bash
gcc -o myapp main.o -L./lib -lmylib -Wl,-rpath,'$ORIGIN/../lib'
```

Now the binary finds `lib/libmylib.so` relative to its own location, wherever that location is. Put the tree in `/usr`, in `/opt`, in your home directory, on a USB stick: the libraries are found. The single quotes matter, so the shell does not try to expand `$ORIGIN` itself. You can inspect what a binary carries with:

```bash
readelf -d myapp | grep -i rpath
```

## The Data Path: Find Yourself at Run Time

For everything else the program has to compute its prefix instead of assuming it. On Linux the executable's own path is available through `/proc`:

```c
char exe[PATH_MAX];
ssize_t n = readlink("/proc/self/exe", exe, sizeof(exe) - 1);
exe[n] = '\0';
/* dirname(exe) is bin/, so the prefix is one level up */
```

From there `share/`, `etc/` and `lib/` are relative paths. The whole tree becomes a self-contained unit that works from anywhere. Windows and macOS programs have done this since forever, which is why an application there is a folder you can drag; Unix programs could have done it all along and mostly chose not to.

There is a portable detail: `/proc/self/exe` is Linux. On other systems there are equivalents, and `argv[0]` plus `PATH` is the fallback of last resort. A small function in the program's startup handles all of it once.

## Why Unix Fought This

The Filesystem Hierarchy Standard was designed for a different problem. It wanted every binary in `/usr/bin`, every library in `/usr/lib`, every configuration file in `/etc`, so that a system administrator could find anything without knowing which package it came from, share `/usr` read-only across machines, and put `/var` on a disk that could fill up without taking the system down. Those were good goals for a multi-user machine with one administrator and a small number of packages, all installed from one source.

**The hierarchy optimised for the administrator's view of the machine, at the cost of the program's independence from it.** Once a package is scattered across six directories, it can only work in exactly that configuration, and the package manager becomes the only thing that knows how to reassemble it. That is fine as long as there is one package manager and everything goes through it. It stops being fine the moment you want two versions of something, or a version the distribution does not ship, or to hand a program to someone as a single thing.

## What Came Later

The pressure did not go away, and the answers that appeared later are all forms of relocation. Self-contained application bundles for Linux, a whole tree in one file that mounts itself and runs from wherever it is, are `$ORIGIN` plus a run-time prefix taken to their conclusion. Functional package managers that install every package into its own hashed directory and never into `/usr` are the same idea from the other side: nothing is ever at a known location, so everything must locate what it needs by reference rather than by convention. Containers give up on the question entirely and ship the whole filesystem.

Every one of these exists because the original decision, that a program may assume where it lives, was wrong, and the fix is cheap. Link with `$ORIGIN`. Find your own path at start-up. Never write an absolute path into a binary. A program that does these three things installs by being copied, uninstalls by being deleted, and runs in as many versions side by side as you care to keep. That is what installing was supposed to mean.
