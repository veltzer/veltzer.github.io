+++
title = "grep שבור - השתמשו בפרל במקום"
date = 2010-07-02

[taxonomies]
tags = ["פרל", "לינוקס", "שורת-פקודה"]
+++

תוך כדי הרצה של צירופי grep(1) שונים כדי לאתר פגמים בקובצי מקור, נתקלתי בקשיים מובנים של
grep(1). נראה שתחביר הביטויים הרגולריים ב־grep(1) מוגבל מאוד, ולכן עדיף להשתמש בפרל כדי לפתור
את הבעיות האלה, מכיוון שהתמיכה שלו בביטויים רגולריים מצוינת. סקריפט קטן יכול לפתור את כל צורכי
ה־grep שלכם. אז הנה הוא. אתם מוזמנים להעיר עם תיקונים ואשלב אותם, ואם תרצו להוסיף יכולות.

*(הערה: הפוסט הזה יובא מבלוג וורדפרס ישן, והייבוא בלע את תווי ה־`<` בסקריפט — ולקח איתם את
תנאי הלולאה, את ה־`open` ואת שורת ה־`while`. הרשימה שלהלן שוחזרה. שימו לב ששורת ה־`while`
משתמשת ב־`my $line` ולא בסגנון `my($line)` שבשאר הקוד כאן: הצורה עם הסוגריים מכניסה את הקריאה
להקשר רשימה, מה שקורא רק את השורה הראשונה של כל קובץ.)*

```perl
#!/usr/bin/perl -w

# This is a general script to grep using perl to overcome some of the deficiencies
# of grep(1) grepping...

use strict;
use diagnostics;

my($pattern)=$ARGV[0];
my($debug)=0;
my($print_filename)=1;

for(my($i)=1;$i<@ARGV;$i++) {
        my($filename)=$ARGV[$i];
        if($debug) {
                print "doing file [$filename]\n";
        }
        open(FILE,"<",$filename) || die("unable to open file [$filename]: $!");
        while(my $line=<FILE>) {
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
