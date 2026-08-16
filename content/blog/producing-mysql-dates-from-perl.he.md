+++
title = "יצירת תאריכי MySQL מתוך פרל"
date = 2011-04-24

[taxonomies]
tags = ["פרל", "mysql", "תכנות"]
+++

יצא לכם לכתוב סקריפט פרל מזדמן ורציתם להכניס את התאריך והשעה הנוכחיים למסד נתונים של MySQL?
הנה הפונקציה שעושה זאת. זה עובד עבור עמודה מסוג `datetime`.

```perl
# function to return the current time in mysql format
sub mysql_now() {
        my($sec,$min,$hour,$mday,$mon,$year,$wday, $yday,$isdst)=localtime(time);
        my($result)=sprintf("%4d-%02d-%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
        return $result;
}
```
