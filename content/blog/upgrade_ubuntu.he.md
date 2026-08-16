+++
title = "איך לשדרג אובונטו בלי כלי השדרוג שלהם"
date = 2025-09-04

[taxonomies]
tags = ["ubuntu", "linux", "ניהול-מערכות"]
+++

## בעיית השדרוג

לב הבעיה הוא שלפעמים כשמנסים לשדרג אובונטו, השדרוג נכשל. זה קרה לי כשניסיתי לשדרג
ל־`plucky (25.04)`. הכלי פשוט נכשל, וניסיתי לחכות בתקווה שאובונטו יתקנו את הבאג. לא היה מזל.
בסוף החלטתי לשדרג ידנית בעצמי, וזה עבד מצוין.

## פתרון השדרוג הידני

### סנכרון

הדבר הראשון שצריך לעשות הוא להסתנכרן עם הגרסה הקודמת:

```sh
$ sudo apt update
$ sudo apt dist-upgrade
```

### ביטול מאגרים של צד שלישי

הדבר הבא הוא לבטל ידנית כל מקור חבילות שאינו של אובונטו מתוך `/etc/apt/sources.list.d`.
בדרך כלל אני פשוט יוצר תיקייה בשם `/etc/apt/sources.list.moved` ומעביר לשם את הכול חוץ מאובונטו.

### הגדרת מקור אובונטו להפצה החדשה

עדכנו את `/etc/apt/sources.list.d/ubuntu.sources` לתוכן הבא (החליפו את שם ההפצה שלכם):

```txt
Enabled: yes
Types: deb
URIs: http://us.archive.ubuntu.com/ubuntu
Suites: plucky plucky-updates plucky-security plucky-backports
Components: main restricted universe multiverse
Architectures: amd64
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
```

### שדרוג ופתרון הבעיות

```sh
$ sudo apt update
$ sudo apt dist-upgrade
```

תצטרכו לפתור בעיות תוך כדי, אבל הן דברים סטנדרטיים.

### אתחול

וזהו.
