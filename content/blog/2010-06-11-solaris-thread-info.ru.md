+++
title = "Как найти информацию о потоках в Solaris"
description = "Файлы /proc в Solaris двоичные, поэтому этот небольшой скрипт на Perl находит процесс по имени через pgrep и фильтрует вывод ps -eL, оставляя только его потоки."
date = 2010-06-11
slug = "solaris-thread-info"

[taxonomies]
tags = ["системное-администрирование", "perl"]
+++

В ходе крестового похода против ошибок в программе на C++, работающей в системе Solaris, мне понадобилось узнать информацию обо всех потоках, принадлежащих определённому процессу.

Программа написана именно так, потому что информация обо всех потоках в системе нужна редко — обычно нужны потоки конкретного процесса. Другой способ получить эти сведения — файловая система /proc, но, к сожалению (или к счастью?!?), файлы в этой файловой системе Solaris обычно имеют двоичное содержимое, в отличие от текстового, которое обычно встречаешь в системе Linux.

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
