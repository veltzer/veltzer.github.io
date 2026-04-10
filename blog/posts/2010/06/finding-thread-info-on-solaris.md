---
tags:
  - solaris
  - perl
  - sysadmin
date: 2010-06-11
---

# Finding thread info on Solaris

As part of a crusade to find bugs in a C++ program running on a Solaris system I needed to find out information about all the threads belonging to a certain process.

The program is written the way it is because you rarely need thread info about all threads running in a system but rather threads limited to a certain process. A different way to get this info is through the /proc file system but unfortunately (or fortunately ?!?) files in this Solaris file system usually have binary content as opposed to the textual content that one usually finds on a Linux system.

```perl
#!/usr/bin/perl -w

# Give this script the name of a process and it will show you thread
# infomation about your process...

use strict;
use diagnostics;

if(@ARGV<1) {
    die("usage myps.pl [process names...]");
}

for(my($p)=0;$p<@ARGV;$p++) {
    my($pname)=$ARGV[$p];
    print "showing diagnostics information for process $pname\
";

    # first lets find out the pid of the process
    my($pid)=`pgrep $pname`;
    chop($pid);
    print "The process id of the process is $pid\
";

    # now lets print all the thread info for that process...
    my(@lines)=`ps -eL`;
    for(my($i)=0;$i<@lines;$i++) {
        my($line)=$lines[$i];
        my(@fields)=split(" ",$line);
        if($fields[0] eq $pid) {
            print $line;
            #print(join('-',@fields));
        }
    }
}
```
