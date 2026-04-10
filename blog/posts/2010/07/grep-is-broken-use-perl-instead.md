---
tags:
  - perl
  - linux
  - command-line
date: 2010-07-02
---

# Grep is broken - use perl instead

In the course of running various grep(1) combination to find various defects in source files I ran into inherent grep(1) difficulties. It seems that the regular expression syntax in grep(1) is very limited and so it's better to use perl to solve these issues as it's regular expression support is fantastic. A small script can solve all your grepping needs. So here it is. Please comment with fixes and I'll incorporate them if you want to add features.

```perl
#!/usr/bin/perl -w

# This is a general script to grep using perl to overcome some of the deficiencies
# of grep(1) grepping...

use strict;
use diagnostics;

my($pattern)=$ARGV[0];
my($debug)=0;
my($print_filename)=1;

for(my($i)=1;$i) {
                if($line=~$pattern) {
                        if($print_filename) {
                                print $filename.": ";
                        }
                        print $line;
                }
        }
        close(FILE) || die("unable to close file [$filename]: $!");
}
```
