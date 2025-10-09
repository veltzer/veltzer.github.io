---
date: 2025-09-04
---

# How to upgrade Ubuntu without their upgrade tool

## The problem

The heart of the problem is that sometimes when you try to upgrade ubuntu the upgrade fails.
This happened to me when trying to upgrade to `plucky (25.04)`. The tool would just fail and
I tried waiting it out hoping that ubuntu will solve the bug. No such luck. Finally
I decided to upgrade it myself manually and it worked like a charm.

## The solution

### Sync up

The first thing you need to do is sync up with the previous release:

```sh
$ sudo apt update
$ sudo apt dist-upgrade
```

### Disable third party repos

The next thing is to manually disable any non ubuntu source of packages from `/etc/apt/sources.list.d`.
I usually just create a folder called `/etc/apt/sources.list.moved` and move all but ubuntu there.

### Setup the ubuntu source to the new distribution

update `/etc/apt/sources.list.d/ubuntu.sources` to the following content (replace your distro name):

```txt
Enabled: yes
Types: deb
URIs: http://us.archive.ubuntu.com/ubuntu
Suites: plucky plucky-updates plucky-security plucky-backports
Components: main restricted universe multiverse
Architectures: amd64
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
```

### Upgrade and solve all issues

```sh
$ sudo apt update
$ sudo apt dist-upgrade
```

You will need to solve issues along the way but they are standard things.

### Reboot

And that's it.
