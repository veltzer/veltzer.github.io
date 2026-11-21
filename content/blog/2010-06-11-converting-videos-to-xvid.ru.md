+++
title = "Перекодирование видео в xvid в Linux"
description = "Скрипт на bash, который с помощью mencoder перекодирует видео в кодек xvid на месте, чтобы оно играло на PS3, и останавливается на первом файле, который не удалось обработать."
date = 2010-06-11
slug = "converting-videos-to-xvid"

[taxonomies]
tags = ["linux", "видео"]
+++

Я хотел перекодировать несколько видеофайлов в своей системе Linux в кодек xvid, чтобы смотреть их на PS3. Решение, которое я нашёл, — пакет mencoder.

```bash
#!/bin/bash

# this script converts videos given to it to the xvid codec, IN PLACE,
# this means it replaces the original files...

for x in "$@"; do
    echo "$x"
    y="$x.tmp"
    mencoder "$x" -ovc xvid -oac copy -xvidencopts fixed_quant=4 -o "$y"
    ret=$?
    if [[ $ret -eq 0 ]]; then
        mv "$y" "$x"
        ret=$?
        if [[ $ret -ne 0 ]]; then
            echo "problem moving file $x"
            break
        fi
    else
        echo "problem converting file $x"
        break
    fi
done
```
