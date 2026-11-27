+++
date = 2010-06-24
description = "One dpkg command line purges every package left in the rc state, removed but with its configuration files still on the system."
slug = "purging-unneeded-debian-packages"
title = "Purging unneeded packages on a debian system"

[taxonomies]
tags = ["linux", "debian"]
+++

If you want to remove all packages which are in the "rc" state (means that the package was already removed but only it's configuration remained) you can use the following command as administrator:

`dpkg --purge`dpkg --list | grep "^rc" | tr -s " " | cut -d " " -f 2``

Take care to save configuration files that you need before issuing it.
