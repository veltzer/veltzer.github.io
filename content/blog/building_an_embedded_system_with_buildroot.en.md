+++
title = "Buildroot Is the Fastest Way From a Bare Board to a Booting Linux"
date = 2014-02-16

[taxonomies]
tags = ["linux", "embedded"]
+++

An embedded Linux system is four things: a cross-compilation toolchain, a bootloader, a kernel, and a root filesystem with exactly the programs you need and nothing else. You can assemble each by hand. People did, for years, and every one of them wrote a pile of shell scripts that only they understood. Buildroot is the pile of scripts done once, properly, for everyone.

**Buildroot takes one configuration file and produces every one of those four things, reproducibly, from source.** This post is the shortest tour I can give of how that works.

## Getting It

Download a release tarball or clone the repository, and unpack it somewhere with a lot of disk space. Builds are large, because the toolchain is built from source too.

```bash
wget https://buildroot.org/downloads/buildroot-2014.02.tar.gz
tar xzf buildroot-2014.02.tar.gz
cd buildroot-2014.02
```

You need the usual host tools: a C compiler, `make`, `patch`, `wget`, and the development headers for `ncurses` if you want the menu interface. Buildroot checks for them and tells you what is missing.

## Start From a Defconfig

Buildroot ships a default configuration for many common boards. List them:

```bash
make list-defconfigs
```

Pick the one closest to your hardware and load it. For a Raspberry Pi, for instance:

```bash
make raspberrypi_defconfig
```

This writes a `.config` file at the top of the tree. Everything that follows reads it. If your board is not in the list, start from the nearest relative and change the architecture and the kernel settings; that is still far less work than starting from nothing.

## Adjust With Menuconfig

```bash
make menuconfig
```

The menu is the same one the kernel uses, and it is organised by the four components above:

- **Target options**: architecture, CPU variant, floating-point ABI.
- **Toolchain**: build one from source, or point at an external one you already have. Building takes longer once; the external route is faster but you inherit its choices of C library and kernel headers.
- **Kernel**: which version, which defconfig, whether to build a device tree.
- **Bootloader**: U-Boot, Barebox, or none if the board has its own.
- **Target packages**: the software that goes into the root filesystem. Busybox is on by default and gives you a shell and the standard utilities in one small binary. Everything else is opt-in.
- **Filesystem images**: ext4, squashfs, a tarball, an initramfs.

Save and exit. The `.config` file is the only state, so keep it in version control.

## Build

```bash
make
```

Go and do something else. The first build fetches every source tarball, builds the toolchain, then the kernel, then every package, then assembles the root filesystem and packs it into an image. Later builds are incremental and much faster.

When it finishes, everything you want is in one directory:

```text
output/images/
```

You will find the kernel image, the device tree blob if any, the bootloader, and the root filesystem in whatever format you chose. Writing them to an SD card or flashing them to the board depends on the board, and the defconfig usually comes with a `readme.txt` in `board/<vendor>/<board>/` that says how.

## Adding a Package

Suppose you need a program Buildroot does not know. Every package is a directory under `package/` with two files. A `Config.in` that adds it to the menu:

```text
config BR2_PACKAGE_HELLO
	bool "hello"
	help
	  A small example program.
```

and a `hello.mk` that says where the source comes from and how to build it:

```makefile
HELLO_VERSION = 1.0
HELLO_SITE = http://example.org/downloads
HELLO_LICENSE = GPL-2.0

$(eval $(autotools-package))
```

If the program uses autotools, that last line is the whole build recipe. There are equivalents for CMake, plain Makefiles, Python packages and a few more. Add a `source "package/hello/Config.in"` line to `package/Config.in`, run `make menuconfig`, tick the box, and rebuild.

## Buildroot or Yocto

The other serious option is Yocto, and the comparison comes down to one question: **is this one product or a family of products?**

Buildroot builds one image from one configuration. It is simple to understand, the whole thing is plain `make` and Kconfig, a newcomer is productive in a day, and rebuilding from scratch is the answer to most problems. It does not do binary packages, it does not manage several images that share layers, and if you change the configuration substantially you rebuild everything.

Yocto builds a package feed and composes images from it. It handles product families, updates and layers of vendor support, and its learning curve is measured in weeks. For a team shipping a line of related devices it is the right tool. For one board, one image, and one person who wants it booting this afternoon, it is a great deal of machinery to carry.

I reach for Buildroot first and move only when the project proves it needs more. Most never do.
