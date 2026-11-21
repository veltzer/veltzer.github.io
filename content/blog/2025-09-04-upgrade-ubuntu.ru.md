+++
title = "Как обновить Ubuntu без их инструмента обновления"
description = "Когда инструмент обновления Ubuntu отказывает, как это случилось с plucky (25.04), обновляйтесь вручную: уберите сторонние репозитории, направьте ubuntu.sources на новый релиз и сделайте dist-upgrade."
date = 2025-09-04
slug = "upgrade-ubuntu"

[taxonomies]
tags = ["ubuntu", "linux", "системное-администрирование"]
+++

## Проблема обновления

Суть проблемы в том, что иногда, когда пытаешься обновить ubuntu, обновление проваливается.
Так случилось со мной при попытке обновиться до `plucky (25.04)`. Инструмент просто падал,
и я пытался переждать в надежде, что ubuntu исправит ошибку. Не повезло. В конце концов
я решил обновить систему сам, вручную, и всё сработало как по маслу.

## Решение: ручное обновление

### Синхронизация

Первое, что нужно сделать, — синхронизироваться с предыдущим релизом:

```sh
$ sudo apt update
$ sudo apt dist-upgrade
```

### Отключите сторонние репозитории

Далее нужно вручную отключить все источники пакетов, не относящиеся к ubuntu, в `/etc/apt/sources.list.d`.
Обычно я просто создаю папку `/etc/apt/sources.list.moved` и переношу туда всё, кроме ubuntu.

### Направьте источник ubuntu на новый дистрибутив

Приведите `/etc/apt/sources.list.d/ubuntu.sources` к следующему содержимому (подставьте имя своего дистрибутива):

```txt
Enabled: yes
Types: deb
URIs: http://us.archive.ubuntu.com/ubuntu
Suites: plucky plucky-updates plucky-security plucky-backports
Components: main restricted universe multiverse
Architectures: amd64
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
```

### Обновитесь и решите все проблемы

```sh
$ sudo apt update
$ sudo apt dist-upgrade
```

По ходу придётся решать проблемы, но это стандартные вещи.

### Перезагрузка

Вот и всё.
