---
tags:
  - perl
  - mysql
  - programming
date: 2011-04-24
---

# Producing MySQL dates from Perl

Ever written the occasional Perl script and wanted to insert the current date and time into a MySQL database? Here is the function to do it. This works for a column of type 'datetime'.

```perl
# function to return the current time in mysql format
sub mysql_now() {
        my($sec,$min,$hour,$mday,$mon,$year,$wday, $yday,$isdst)=localtime(time);
        my($result)=sprintf("%4d-%02d-%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
        return $result;
}
```
