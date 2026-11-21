+++
title = "Переход с Google-Chrome на Firefox в Linux"
description = "Google-Chrome в Linux шпионит за вами, жжёт процессор и изнашивает диск лишними записями. Переходите на Firefox; скрипт перечисляет настройки, которые нужно поменять при переезде."
date = 2025-09-01
slug = "chrome-to-firefox"

[taxonomies]
tags = ["браузер", "linux", "безопасность"]
+++

## Проблемы Google-Chrome

У Google-Chrome есть несколько проблем, часть из них специфична для Linux, часть — нет

* Google-Chrome шпионит за вами и отправляет слишком много информации Google и рекламодателям.
* Google-Chrome в Linux потребляет слишком много процессорного времени, и его отзывчивость намного хуже, чем у Firefox. Я действительно видел это на сайтах для тренировки слепой печати.
* Google-Chrome в Linux пишет на диск слишком много и изнашивает его. Это известная проблема https://unix.stackexchange.com/questions/438456/google-chrome-high-i-o-writes

Итог всего этого: в Linux я рекомендую Firefox, а не Google-Chrome.

Я написал скрипт `browser_move_to_firefox.sh`, в котором видны все настройки, которые нужно изменить при переходе на другой браузер.
