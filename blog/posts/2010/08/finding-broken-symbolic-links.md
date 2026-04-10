---
tags:
  - linux
  - filesystem
  - command-line
date: 2010-08-13
---

# Finding broken symbolic links

I sometimes need to find all broken symbolic links in a folder, recursively or not. `find(1)` is the all UNIX right tool for the job as far as finding files is concerned but it does not have an explicit `-and -type brokenlink` option...

Some solutions involve sending the output of `find(1)` to some other tool. These solutions are sub-optimal in that once you leave the comfort of `find(1)` you give up the ability to use many of it's fine features and run into other problems (file names with white space characters just to name one such problem).

Other solutions involve doing `find -L . -type l` which forces `find(1)` to follow all symbolic links and ultimately only print those which it cannot follow. This solution has other drawbacks. One is that you do not necessarily want `find(1)` to follow every symbolic link since this may cause it to wander to huge areas of your hard drive that you do not wish to scan. Another deficiency is the fact that there is a difference between a symbolic link that cannot be followed and one which cannot be read.

My solution is this:
`find . -type l -and -not -exec test -e {} \; -print`
