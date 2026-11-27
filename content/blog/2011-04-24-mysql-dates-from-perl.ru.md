+++
date = 2011-04-24
description = "Небольшая функция на Perl, форматирующая текущее местное время как строку datetime для MySQL, готовую для вставки в столбец типа datetime."
slug = "mysql-dates-from-perl"
title = "Получение дат в формате MySQL на Perl"

[taxonomies]
tags = ["perl", "mysql", "программирование"]
+++

Случалось ли вам писать небольшой скрипт на Perl и захотеть вставить текущие дату и время в базу данных MySQL? Вот функция, которая это делает. Она подходит для столбца типа `datetime`.

```perl
# function to return the current time in mysql format
sub mysql_now() {
        my($sec,$min,$hour,$mday,$mon,$year,$wday, $yday,$isdst)=localtime(time);
        my($result)=sprintf("%4d-%02d-%02d %02d:%02d:%02d",$year+1900,$mon+1,$mday,$hour,$min,$sec);
        return $result;
}
```
