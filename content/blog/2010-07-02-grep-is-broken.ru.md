+++
title = "Grep сломан — используйте perl"
description = "Синтаксис регулярных выражений grep слишком беден для поиска дефектов в исходниках, поэтому вот короткий скрипт на Perl, который ищет с помощью куда лучших регулярных выражений Perl."
date = 2010-07-02
slug = "grep-is-broken"

[taxonomies]
tags = ["perl", "linux", "командная-строка"]
+++

Перебирая различные комбинации grep(1) в поисках разнообразных дефектов в исходных файлах, я столкнулся с неустранимыми трудностями самого grep(1). Синтаксис регулярных выражений в grep(1), похоже, очень ограничен, и поэтому такие задачи лучше решать на perl, у которого поддержка регулярных выражений фантастическая. Небольшой скрипт закроет все ваши потребности в grep. Вот он. Если хотите добавить возможности, пишите исправления в комментариях — я их включу.

*(Примечание: этот пост был импортирован из старого блога на WordPress, и при импорте
пропали символы `<` в скрипте — вместе с ними исчезли условие цикла, `open` и строка
`while`. Приведённый ниже листинг восстановлен. Обратите внимание, что в строке `while`
используется `my $line`, а не стиль `my($line)`, принятый здесь в остальных местах:
форма со скобками ставит чтение строки в списочный контекст, и тогда из каждого файла
читается только первая строка.)*

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
