+++
title = "מציאת מידע על תהליכונים בסולאריס"
date = 2010-06-11

[taxonomies]
tags = ["solaris", "perl", "sysadmin"]
+++

כחלק ממסע צלב לאיתור באגים בתוכנית C++ שרצה על מערכת סולאריס, הייתי צריך למצוא מידע על כל
התהליכונים (threads) השייכים לתהליך מסוים.

התוכנית כתובה כפי שהיא משום שלעיתים רחוקות צריך מידע על כל התהליכונים שרצים במערכת, אלא דווקא
על תהליכונים המוגבלים לתהליך מסוים. דרך אחרת לקבל את המידע הזה היא דרך מערכת הקבצים ‎/proc,
אבל לרוע המזל (או למזל?!) קבצים במערכת הקבצים הזו בסולאריס מכילים בדרך כלל תוכן בינארי, בניגוד
לתוכן הטקסטואלי שנהוג למצוא במערכת לינוקס.

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
