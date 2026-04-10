---
tags:
  - linux
  - performance
  - filesystem
date: 2010-07-24
---

# Using "noatime" on a running Linux system

When upgrading my Ubuntu system my `/etc/fstab` got overwritten by the upgrade process. It seems that the new `/etc/fstab` file did not keep my old preferences for file systems. I didn't notice this for some time but what I did notice was that my system was sluggish. After some time I recalled that I had previously used `noatime` as a mount option for all of my hard drives which gave me some more speed and treated my hard drives with a softer touch.

First lets explain what `noatime` means. `atime` or Access Time is an attribute stored by all well behaved UNIX file systems for each and every file. It is one of 3 dates stored: meta info modification time - `ctime`, last modification time - `mtime` and last acces time - `atime`. Out of the 3 atime is the most controversial since it means that for every read from the disk there is a write operation. This is one of the worst defaults in your UNIX system.

The solution is just to disable atime altogether. Warning - this may cause some weird applications that rely on atime to break. If you want your system to be as "default" as possible don't do what I suggest. If you want better performance and hard disk lifetime and on the other hand don't mind parting ways with one or two misfit applications then this trick is for you.

How do you do it? Just edit `/etc/fstab` and add `noatime` at the 4'th column where file system mount options are for any file system you want to avoid access time updating. Reboot your system. Run `mount(1)` to see that all your file systems are mounted correctly. Enjoy.

What applications break? Actually - I have yet to see an application break because of this change. I have been running with "noatime" for 2 years now and all the applications seem to behave well. If you know of an application that breaks please let me know...
