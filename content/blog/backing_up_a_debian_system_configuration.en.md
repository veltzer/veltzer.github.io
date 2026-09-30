+++
title = "Backing Up a Debian System's Configuration, Not Its Bytes"
date = 2012-08-12

[taxonomies]
tags = ["linux", "debian", "sysadmin"]
+++

Most backup advice tells you to copy your files. That is right for your data, but it is the wrong model for the system itself. A Debian or Ubuntu install is almost entirely reconstructible from the archive: the packages are out there, ready to be reinstalled. What is not reconstructible is the small set of decisions you made, and those are what a system backup should capture. Three things are enough to rebuild a machine's personality.

## The Three Commands

```bash
# 1. The configuration you edited: everything under /etc.
sudo tar --create --bzip2 --absolute-names \
    --file "/tmp/etc.$HOSTNAME.tar.bz2" /etc
cp "/tmp/etc.$HOSTNAME.tar.bz2" "$FOLDER"
sudo rm "/tmp/etc.$HOSTNAME.tar.bz2"

# 2. Which packages are installed. Any user can run this.
dpkg --get-selections > "$FOLDER/dpkg_selections.$HOSTNAME.txt"

# 3. Which alternative each choice points at (editor, java, and so on).
update-alternatives --get-selections > "$FOLDER/alternatives.$HOSTNAME.txt"
```

Set `FOLDER` to wherever your backups live before running it.

## What Each Line Is For

**The tar of `/etc`** captures the configuration you actually touched: network settings, fstab, ssh keys and config, cron jobs, package configuration you edited. This is the irreplaceable part, because it is the part you cannot download. `--bzip2` compresses it, and `--absolute-names` keeps the leading slash so you know these are absolute paths; extract deliberately rather than into a live `/`. The build in `/tmp` and copy out afterwards is so the archive is assembled on fast local disk before it lands on whatever `FOLDER` points to, which might be a slow network share. The `sudo` is because much of `/etc` is readable only by root.

**`dpkg --get-selections`** writes the full list of installed packages. This is the manifest of everything you added on top of the base install, and it is tiny, because it is names rather than contents.

**`update-alternatives --get-selections`** records which program each alternative resolves to, so that after a restore `editor` is still the editor you chose and `java` is still the JDK you meant.

## Restoring

On a fresh install of the same release, restore in the same order:

```bash
# Reinstall the same set of packages.
sudo dpkg --set-selections < dpkg_selections.$HOSTNAME.txt
sudo apt-get dselect-upgrade

# Restore the alternatives.
sudo update-alternatives --set-selections < alternatives.$HOSTNAME.txt

# Put back the configuration, carefully, into a mounted target
# rather than over your running /etc.
sudo tar --extract --bzip2 --file etc.$HOSTNAME.tar.bz2 -C /mnt/newroot
```

The one caution is the last step. Do not untar `/etc` straight over a running system without looking; extract into a mounted target, or into a scratch directory, and copy across the files you actually want. Package versions move on, and a config from an older release can confuse a newer daemon.

## Why This Beats a Disk Image

A disk image is larger, is tied to the exact hardware and partition layout, and captures a great deal you do not care about. These three files are a few megabytes, are human-readable, survive a hardware change, and let you rebuild on a newer release by reading the differences rather than fighting them. The bytes of the system are Debian's problem. The decisions are yours, and the decisions are all you need to keep.
